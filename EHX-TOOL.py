#!/usr/bin/env python3
# MN TooL 2025 - Pro Password Cracker
# Developed by Man Yonatan - Use Ethically!

import os
import sys
import time
import hashlib
import itertools
import zipfile
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, IntPrompt

console = Console()

# ─────────────── HASH TYPES ───────────────
HASH_TYPES = {
    "1": ("MD5", hashlib.md5),
    "2": ("SHA1", hashlib.sha1),
    "3": ("SHA256", hashlib.sha256),
    "4": ("SHA512", hashlib.sha512)
}

# ─────────────── BANNER ───────────────
BANNER = r"""
          MN TooL 2025 - Password Cracker

███    ███ ███    ██     ████████  ██████   ██████   ██
████  ████ ████   ██        ██    ██    ██ ██    ██  ██
██ ████ ██ ██ ██  ██        ██    ██    ██ ██    ██  ██
██  ██  ██ ██  ██ ██        ██    ██    ██ ██    ██  ██
██      ██ ██   ████        ██     ██████   ██████   ███████

         Developed by $Man Yon - Use Ethically!
"""

# ─────────────── WORDLIST LOADER ───────────────
def load_wordlist(path: Path):
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                pw = line.strip()
                if pw:
                    yield pw
    except Exception as e:
        console.print(f"[red]Failed to read wordlist file: {e}[/red]")

# ─────────────── ZIP CRACKER ───────────────
def crack_zip(path: Path, wordlist: Path):
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        console.print("[red]Invalid ZIP file.[/red]")
        return
    except FileNotFoundError:
        console.print("[red]ZIP file not found.[/red]")
        return

    if not zf.infolist():
        console.print("[red]ZIP file is empty.[/red]")
        return

    console.print("[yellow]Attempting ZIP method...[/yellow]")
    for pw in load_wordlist(wordlist):
        try:
            zf.extractall(pwd=pw.encode("utf-8"))
            console.print(f" [green]ZIP Password Found (zipfile): {pw}[/green]")
            return
        except:
            continue

    if not shutil.which("7z"):
        console.print(" [red]7z is not installed. Install it to support AES-encrypted ZIP files.[/red]")
        return

    for pw in load_wordlist(wordlist):
        result = subprocess.run(["7z", "t", f"-p{pw}", str(path)],
                                capture_output=True, text=True)
        output = result.stdout + result.stderr
        sys.stdout.write(f"\rTrying: {pw}")
        sys.stdout.flush()
        if "Everything is Ok" in output or result.returncode == 0:
            console.print(f" \n[green]ZIP Password Found (7z): {pw}[/green]")
            return

    console.print(" \n[red]ZIP Password not found in wordlist.[/red]")

# ─────────────── RAR CRACKER ───────────────
def crack_rar(path: Path, wordlist: Path):
    if not shutil.which("unrar"):
        console.print(" [red]unrar is not installed or not in PATH.[/red]")
        return

    if not path.is_file():
        console.print(" [red]RAR file not found.[/red]")
        return

    console.print(" [yellow]Starting RAR password cracking...[/yellow]")
    for pw in load_wordlist(wordlist):
        result = subprocess.run(["unrar", "t", f"-p{pw}", str(path)],
                                capture_output=True, text=True)
        if "All OK" in result.stdout:
            console.print(f" [green]RAR Password Found: {pw}[/green]")
            return
        sys.stdout.write(f "\rTrying: {pw}")
        sys.stdout.flush()

    console.print(" \n[red]RAR Password not found in wordlist.[/red]")

# ─────────────── PDF CRACKER ───────────────
def crack_pdf(path: Path, wordlist: Path):
    if not shutil.which("qpdf"):
        console.print("[red]qpdf is not installed. Install it to support PDF cracking.[/red]")
        return

    if not path.is_file():
        console.print(" [red]PDF file not found.[/red]")
        return

    console.print(" [yellow]Starting PDF password cracking with qpdf...[/yellow]")
    for pw in load_wordlist(wordlist):
        result = subprocess.run([
            "qpdf", "--password=" + pw, "--decrypt",
            str(path), "/dev/null"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]PDF Password Found: {pw}[/green]")
            return
        sys.stdout.write(f"\rTrying: {pw}")
        sys.stdout.flush()

    console.print(" \n[red] PDF Password not found in wordlist. [/red] ")

# ─────────────── HASH CRACKING ───────────────
def crack_hash_with_wordlist(target_hash, wordlist_path, hash_func):
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                hashed = hash_func(word.encode()).hexdigest()
                if hashed == target_hash:
                    console.print(f" [green]Password Found:[/green] {word} ")
                    return
        console.print(" [red]Password not found in wordlist.[/red] ")
    except FileNotFoundError:
        console.print(" [red]Wordlist file not found.[/red] ")

# ─────────────── CHOOSE HASH TYPE ───────────────
def choose_hash_type():
    console.print("\n[bold]Select Hash Type:[/bold]")
    for key, (name, _) in HASH_TYPES.items():
        console.print(f"{key}) {name}")
    choice = Prompt.ask("Choice", choices=list(HASH_TYPES.keys()))
    return HASH_TYPES[choice]

# ─────────────── MAIN MENU ───────────────
def main_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        console.print(BANNER)
        console.print("[bold]Main Menu[/bold]")
        console.print("1) ZIP Password Cracker")
        console.print("2) RAR Password Cracker")
        console.print("3) PDF Password Cracker")
        console.print("4) Hash Cracker")
        console.print("5) Exit")

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            path = Path(Prompt.ask("Enter full path to ZIP file")).expanduser()
            wlist = Path(Prompt.ask("Enter full path to wordlist file")).expanduser()
            crack_zip(path, wlist)
            input("\nPress Enter to return to menu...")

        elif choice == "2":
            path = Path(Prompt.ask("Enter full path to RAR file")).expanduser()
            wlist = Path(Prompt.ask("Enter full path to wordlist file")).expanduser()
            crack_rar(path, wlist)
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            path = Path(Prompt.ask("Enter full path to PDF file")).expanduser()
            wlist = Path(Prompt.ask("Enter full path to wordlist file")).expanduser()
            crack_pdf(path, wlist)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            hash_value = Prompt.ask("Enter the hash").strip()
            path = Path(Prompt.ask("Enter full path to wordlist")).expanduser()
            algo_name, hash_func = choose_hash_type()
            crack_hash_with_wordlist(hash_value, path, hash_func)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            console.print("[bold red]Goodbye![/bold red]")
            break

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/red]")