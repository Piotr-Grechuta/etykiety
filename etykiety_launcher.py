import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PROFILES = {
    "Buty": os.path.join(ROOT_DIR, "buty", "etykiety_14.py"),
    "Torby i paski": os.path.join(ROOT_DIR, "Torby_paski", "etykiety_13T3.py"),
}


def run_selected(profile_name: str) -> None:
    script_path = PROFILES.get(profile_name)
    if not script_path or not os.path.exists(script_path):
        messagebox.showerror("Blad", f"Nie znaleziono skryptu dla profilu: {profile_name}")
        return

    run_cwd = os.path.dirname(script_path)
    try:
        subprocess.run([sys.executable, script_path], cwd=run_cwd, check=True)
    except subprocess.CalledProcessError as exc:
        messagebox.showerror("Blad", f"Uruchomienie zakonczone bledem (kod={exc.returncode}).")


def main() -> None:
    root = tk.Tk()
    root.title("Etykiety - wybor profilu")
    root.geometry("420x170")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=16, pady=16)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Wybierz profil etykiet:", font=("Segoe UI", 11, "bold")).pack(anchor="w")

    selected = tk.StringVar(value="Buty")
    option = tk.OptionMenu(frame, selected, *PROFILES.keys())
    option.config(width=28)
    option.pack(anchor="w", pady=(8, 12))

    tk.Label(
        frame,
        text="Program uruchomi odpowiedni generator i okno wyboru pliku DBF/XLSX.",
        fg="#444444",
    ).pack(anchor="w", pady=(0, 10))

    tk.Button(
        frame,
        text="Uruchom",
        width=20,
        command=lambda: run_selected(selected.get()),
    ).pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    main()
