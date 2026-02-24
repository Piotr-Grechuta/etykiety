import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import dictionary_store as store
from dictionary_manager_gui import open_dictionary_manager

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PROFILES = {
    "Buty": {
        "key": "buty",
        "script": os.path.join(ROOT_DIR, "buty", "etykiety_14.py"),
    },
    "Torby i paski": {
        "key": "torby_paski",
        "script": os.path.join(ROOT_DIR, "Torby_paski", "etykiety_13T3.py"),
    },
    "Ubrania": {
        "key": "ubrania",
        # Dla ubrań uzywamy tego samego silnika etykiet co torby/paski,
        # ale z osobnym profilem slownikow.
        "script": os.path.join(ROOT_DIR, "Torby_paski", "etykiety_13T3.py"),
    },
}


def run_selected(profile_name: str) -> None:
    cfg = PROFILES.get(profile_name)
    if not cfg:
        messagebox.showerror("Blad", f"Nieznany profil: {profile_name}")
        return

    script_path = cfg["script"]
    if not os.path.exists(script_path):
        messagebox.showerror("Blad", f"Nie znaleziono skryptu dla profilu: {profile_name}")
        return

    try:
        store.ensure_profile_seeded(cfg["key"])
    except Exception as exc:
        messagebox.showerror("Blad", f"Nie mozna przygotowac slownikow: {exc}")
        return

    run_cwd = os.path.dirname(script_path)
    try:
        env = os.environ.copy()
        env["ETYKIETY_PROFILE"] = cfg["key"]
        subprocess.run([sys.executable, script_path], cwd=run_cwd, env=env, check=True)
    except subprocess.CalledProcessError as exc:
        messagebox.showerror("Blad", f"Uruchomienie zakonczone bledem (kod={exc.returncode}).")


def open_lists_gui(root: tk.Tk, profile_name: str) -> None:
    cfg = PROFILES.get(profile_name)
    if not cfg:
        messagebox.showerror("Blad", f"Nieznany profil: {profile_name}")
        return
    open_dictionary_manager(root, cfg["key"])


def main() -> None:
    # Przy pierwszym uruchomieniu zasila baze z arkuszy XLSX.
    try:
        store.init_all_profiles_from_xlsx()
    except Exception:
        # Blad inicjalizacji obslugujemy pozniej na poziomie akcji.
        pass

    root = tk.Tk()
    root.title("Etykiety - wybor profilu")
    root.geometry("520x240")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Wybierz profil etykiet:", font=("Segoe UI", 11, "bold")).pack(anchor="w")

    selected = tk.StringVar(value="Buty")
    option = tk.OptionMenu(frame, selected, *PROFILES.keys())
    option.config(width=30)
    option.pack(anchor="w", pady=(8, 12))

    tk.Label(
        frame,
        text="Uruchom generator etykiet albo otworz GUI list/slownikow dla wybranego profilu.",
        fg="#444444",
    ).pack(anchor="w", pady=(0, 12))

    btns = tk.Frame(frame)
    btns.pack(anchor="w")

    tk.Button(
        btns,
        text="Uruchom generator",
        width=20,
        command=lambda: run_selected(selected.get()),
    ).pack(side=tk.LEFT)

    tk.Button(
        btns,
        text="Zarzadzaj listami",
        width=20,
        command=lambda: open_lists_gui(root, selected.get()),
    ).pack(side=tk.LEFT, padx=(10, 0))

    tk.Label(
        frame,
        text="Listy sa przechowywane w bazie SQLite: etykiety_slowniki.db (automatycznie zasilane z XLSX).",
        fg="#555555",
    ).pack(anchor="w", pady=(14, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
