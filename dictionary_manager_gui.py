from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

import dictionary_store as store


class RowEditor:
    def __init__(self, parent: tk.Misc, title: str, fields: List[Dict[str, str]], initial: Dict[str, str] | None = None):
        self.result = None
        self._fields = fields
        self._entries: Dict[str, tk.Entry] = {}

        top = tk.Toplevel(parent)
        top.title(title)
        top.resizable(False, False)
        top.transient(parent)
        self._top = top

        frame = tk.Frame(top, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        for i, field in enumerate(fields):
            tk.Label(frame, text=field["label"]).grid(row=i, column=0, sticky="w", padx=(0, 8), pady=4)
            ent = tk.Entry(frame, width=48)
            ent.grid(row=i, column=1, sticky="ew", pady=4)
            self._entries[field["key"]] = ent
            if initial:
                ent.insert(0, str(initial.get(field["key"], "")))

        btns = tk.Frame(frame)
        btns.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(10, 0))

        tk.Button(btns, text="Anuluj", width=12, command=self._cancel).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btns, text="Zapisz", width=12, command=self._save).pack(side=tk.RIGHT)

        first_key = fields[0]["key"]
        self._entries[first_key].focus_set()
        top.grab_set()
        top.protocol("WM_DELETE_WINDOW", self._cancel)
        parent.wait_window(top)

    def _cancel(self) -> None:
        self.result = None
        self._top.destroy()

    def _save(self) -> None:
        values: Dict[str, str] = {}
        for field in self._fields:
            key = field["key"]
            val = self._entries[key].get().strip()
            if field.get("required") and not val:
                messagebox.showerror("Blad", f"Pole '{field['label']}' jest wymagane.", parent=self._top)
                self._entries[key].focus_set()
                return
            values[key] = val

        self.result = values
        self._top.destroy()


class DictionaryManagerWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, profile: str):
        super().__init__(parent)
        self.title("Zarzadzanie slownikami")
        self.geometry("1100x700")

        self.profile_var = tk.StringVar(value=store.normalize_profile(profile))

        top = tk.Frame(self, padx=10, pady=8)
        top.pack(fill=tk.X)

        tk.Label(top, text="Profil:").pack(side=tk.LEFT)
        profile_menu = ttk.Combobox(
            top,
            textvariable=self.profile_var,
            values=["buty", "torby_paski", "ubrania"],
            state="readonly",
            width=18,
        )
        profile_menu.pack(side=tk.LEFT, padx=(8, 10))
        profile_menu.bind("<<ComboboxSelected>>", lambda _e: self.refresh_all())

        tk.Button(top, text="Importuj z XLSX", command=self.import_from_xlsx).pack(side=tk.LEFT)
        tk.Button(top, text="Odswiez", command=self.refresh_all).pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.status_var, fg="#444").pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tabs = {}
        self._build_tabs()
        self.refresh_all()

    def _build_tabs(self) -> None:
        self.tabs["colors"] = self._build_tab(
            title="Kolory",
            columns=[("kod", "Kod"), ("pl", "Nazwa PL"), ("en", "Nazwa EN")],
            fetch=lambda p: store.list_colors(p),
            upsert=lambda p, row: store.upsert_color(p, row["kod"], row["pl"], row["en"]),
            delete=lambda p, row: store.delete_color(p, row["kod"]),
            key_fields=["kod"],
        )

        self.tabs["types"] = self._build_tab(
            title="Rodzaje",
            columns=[("kod", "Kod"), ("pl", "Nazwa PL"), ("en", "Nazwa EN")],
            fetch=lambda p: store.list_types(p),
            upsert=lambda p, row: store.upsert_type(p, row["kod"], row["pl"], row["en"]),
            delete=lambda p, row: store.delete_type(p, row["kod"]),
            key_fields=["kod"],
        )

        self.tabs["sizes"] = self._build_tab(
            title="Rozmiary",
            columns=[
                ("rodzaj", "Rodzaj"),
                ("size", "Size"),
                ("eu", "EU"),
                ("uk", "UK"),
                ("us", "US"),
                ("fr", "FR"),
                ("it", "IT"),
            ],
            fetch=lambda p: store.list_sizes(p),
            upsert=lambda p, row: store.upsert_size(
                p,
                row["rodzaj"],
                row["size"],
                row["eu"],
                row["uk"],
                row["us"],
                row["fr"],
                row["it"],
                row.get("_id", ""),
            ),
            delete=lambda p, row: store.delete_size(p, row.get("_id", "")),
            key_fields=["rodzaj", "size"],
        )

    def _build_tab(self, title, columns, fetch, upsert, delete, key_fields):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=title)

        toolbar = tk.Frame(tab, pady=6)
        toolbar.pack(fill=tk.X, padx=8)

        tree = ttk.Treeview(tab, columns=[c[0] for c in columns], show="headings", height=22)
        for key, label in columns:
            tree.heading(key, text=label)
            tree.column(key, width=140, anchor="w")
        tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        scroll = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        cfg = {
            "columns": columns,
            "tree": tree,
            "fetch": fetch,
            "upsert": upsert,
            "delete": delete,
            "key_fields": key_fields,
        }

        tk.Button(toolbar, text="Dodaj", command=lambda c=cfg: self._add_row(c)).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Edytuj", command=lambda c=cfg: self._edit_row(c)).pack(side=tk.LEFT, padx=(6, 0))
        tk.Button(toolbar, text="Usun", command=lambda c=cfg: self._delete_row(c)).pack(side=tk.LEFT, padx=(6, 0))
        tk.Button(toolbar, text="Odswiez", command=lambda c=cfg: self._refresh_tab(c)).pack(side=tk.LEFT, padx=(6, 0))

        return cfg

    def _current_profile(self) -> str:
        return store.normalize_profile(self.profile_var.get())

    def _refresh_tab(self, cfg) -> None:
        profile = self._current_profile()
        tree = cfg["tree"]
        for iid in tree.get_children():
            tree.delete(iid)

        rows = cfg["fetch"](profile)
        for row in rows:
            values = [row.get(key, "") for key, _ in cfg["columns"]]
            iid = row.get("id") or ""
            if iid:
                tree.insert("", tk.END, iid=str(iid), values=values)
            else:
                tree.insert("", tk.END, values=values)

        self.status_var.set(f"Profil: {profile} | Wiersze: {len(rows)}")

    def refresh_all(self) -> None:
        for cfg in self.tabs.values():
            self._refresh_tab(cfg)

    def _selected_row(self, cfg):
        tree = cfg["tree"]
        selected = tree.selection()
        if not selected:
            return None
        values = tree.item(selected[0], "values")
        out = {}
        for i, (key, _label) in enumerate(cfg["columns"]):
            out[key] = values[i] if i < len(values) else ""
        out["_id"] = str(selected[0])
        return out

    def _add_row(self, cfg) -> None:
        fields = [{"key": k, "label": lbl, "required": k in cfg["key_fields"]} for k, lbl in cfg["columns"]]
        editor = RowEditor(self, "Dodaj rekord", fields)
        if not editor.result:
            return
        cfg["upsert"](self._current_profile(), editor.result)
        self._refresh_tab(cfg)

    def _edit_row(self, cfg) -> None:
        selected = self._selected_row(cfg)
        if not selected:
            messagebox.showinfo("Info", "Zaznacz rekord do edycji.", parent=self)
            return

        fields = [{"key": k, "label": lbl, "required": k in cfg["key_fields"]} for k, lbl in cfg["columns"]]
        editor = RowEditor(self, "Edytuj rekord", fields, selected)
        if not editor.result:
            return
        cfg["upsert"](self._current_profile(), editor.result)
        self._refresh_tab(cfg)

    def _delete_row(self, cfg) -> None:
        selected = self._selected_row(cfg)
        if not selected:
            messagebox.showinfo("Info", "Zaznacz rekord do usuniecia.", parent=self)
            return
        if not messagebox.askyesno("Potwierdzenie", "Usun zaznaczony rekord?", parent=self):
            return
        cfg["delete"](self._current_profile(), selected)
        self._refresh_tab(cfg)

    def import_from_xlsx(self) -> None:
        profile = self._current_profile()
        counts = store.import_profile_from_xlsx(profile, replace_existing=True)
        self.refresh_all()
        messagebox.showinfo(
            "Import zakonczony",
            f"Profil: {profile}\nKolory: {counts['colors']}\nRodzaje: {counts['types']}\nRozmiary: {counts['sizes']}",
            parent=self,
        )


def open_dictionary_manager(parent: tk.Misc, profile: str) -> DictionaryManagerWindow:
    return DictionaryManagerWindow(parent, profile)
