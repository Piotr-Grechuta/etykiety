from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT_DIR / "etykiety_slowniki.db"

_PROFILE_DIRS = {
    "buty": "buty",
    "torby_paski": "Torby_paski",
    "torby i paski": "Torby_paski",
    "torby_i_paski": "Torby_paski",
    "ubrania": "ubrania",
    "ubranie": "ubrania",
}


def normalize_profile(profile: str) -> str:
    key = (profile or "").strip().lower().replace("-", "_")
    if key in _PROFILE_DIRS:
        mapped = _PROFILE_DIRS[key]
        if mapped == "buty":
            return "buty"
        if mapped == "ubrania":
            return "ubrania"
        return "torby_paski"
    if "torb" in key or "pask" in key:
        return "torby_paski"
    if "ubra" in key:
        return "ubrania"
    return "buty"


def profile_folder(profile: str) -> Path:
    key = normalize_profile(profile)
    if key == "buty":
        return ROOT_DIR / "buty"
    if key == "ubrania":
        return ROOT_DIR / "ubrania"
    return ROOT_DIR / "Torby_paski"


def _dictionary_sources(profile: str) -> Dict[str, Tuple[str, str]]:
    """
    Mapowanie plikow/sheetow slownikowych dla profilu.
    """
    key = normalize_profile(profile)
    if key == "ubrania":
        return {
            "colors": ("TABELA KOLORÓW.xlsx", "Kolory"),
            "types": ("GRUPY TOWAROWE.xlsx", "Rodzaje"),
            "sizes": ("TABELA ROZMIARÓW.xlsx", "Rozmiary"),
        }
    return {
        "colors": ("Kolory.xlsx", "Kolory"),
        "types": ("Rodzaje.xlsx", "Rodzaje"),
        "sizes": ("Rozmiary.xlsx", "Rozmiary"),
    }


def _db_path(db_path: Optional[Path] = None) -> Path:
    return Path(db_path) if db_path else DEFAULT_DB_PATH


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _to_text(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def _to_sort_value(value: object) -> Optional[float]:
    txt = _to_text(value).replace(",", ".")
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        return None


def _migrate_sizes_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sizes'")
    if not cur.fetchone():
        return

    cur.execute("PRAGMA table_info(sizes)")
    cols = [r["name"] for r in cur.fetchall()]
    if "id" in cols:
        return

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sizes_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT NOT NULL,
            rodzaj TEXT NOT NULL,
            size_value TEXT NOT NULL,
            eu TEXT,
            uk TEXT,
            us TEXT,
            fr TEXT,
            it TEXT,
            sort_value REAL
        )
        """
    )
    cur.execute(
        """
        INSERT INTO sizes_new(profile, rodzaj, size_value, eu, uk, us, fr, it, sort_value)
        SELECT profile, rodzaj, size_value, eu, uk, us, fr, it, sort_value
        FROM sizes
        """
    )
    cur.execute("DROP TABLE sizes")
    cur.execute("ALTER TABLE sizes_new RENAME TO sizes")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sizes_profile_sort ON sizes(profile, sort_value)")


def ensure_schema(db_path: Optional[Path] = None) -> None:
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS colors (
                profile TEXT NOT NULL,
                kod TEXT NOT NULL,
                nazwa_pl TEXT NOT NULL,
                nazwa_en TEXT,
                PRIMARY KEY (profile, kod)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS product_types (
                profile TEXT NOT NULL,
                kod TEXT NOT NULL,
                nazwa_pl TEXT NOT NULL,
                nazwa_en TEXT,
                PRIMARY KEY (profile, kod)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sizes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile TEXT NOT NULL,
                rodzaj TEXT NOT NULL,
                size_value TEXT NOT NULL,
                eu TEXT,
                uk TEXT,
                us TEXT,
                fr TEXT,
                it TEXT,
                sort_value REAL
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sizes_profile_sort ON sizes(profile, sort_value)")
        _migrate_sizes_schema(conn)
        conn.commit()
    finally:
        conn.close()


def import_profile_from_xlsx(profile: str, replace_existing: bool = True, db_path: Optional[Path] = None) -> Dict[str, int]:
    ensure_schema(db_path)
    pkey = normalize_profile(profile)
    pdir = profile_folder(pkey)
    sources = _dictionary_sources(pkey)

    kolory_file, kolory_sheet = sources["colors"]
    rodzaje_file, rodzaje_sheet = sources["types"]
    rozmiary_file, rozmiary_sheet = sources["sizes"]

    kolory = pd.read_excel(pdir / kolory_file, sheet_name=kolory_sheet)
    rodzaje = pd.read_excel(pdir / rodzaje_file, sheet_name=rodzaje_sheet)
    rozmiary = pd.read_excel(pdir / rozmiary_file, sheet_name=rozmiary_sheet)

    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        if replace_existing:
            cur.execute("DELETE FROM colors WHERE profile = ?", (pkey,))
            cur.execute("DELETE FROM product_types WHERE profile = ?", (pkey,))
            cur.execute("DELETE FROM sizes WHERE profile = ?", (pkey,))

        color_rows = []
        for _, row in kolory.iterrows():
            color_rows.append(
                (
                    pkey,
                    _to_text(row.get("KOD_KOLOR")),
                    _to_text(row.get("NAZWA_POLSKA_KOLOR")),
                    _to_text(row.get("NAZWA_ANGIELSKA_KOLOR")),
                )
            )

        type_rows = []
        for _, row in rodzaje.iterrows():
            type_rows.append(
                (
                    pkey,
                    _to_text(row.get("KOD_RODZAJE")),
                    _to_text(row.get("NAZWA_POLSKA_RODZAJE")),
                    _to_text(row.get("NAZWA_ANGIELSKA_RODZAJE")),
                )
            )

        size_rows = []
        for _, row in rozmiary.iterrows():
            size_rows.append(
                (
                    pkey,
                    _to_text(row.get("Rodzaj")),
                    _to_text(row.get("Size")),
                    _to_text(row.get("EU")),
                    _to_text(row.get("UK")),
                    _to_text(row.get("US")),
                    _to_text(row.get("FR")),
                    _to_text(row.get("IT")),
                    _to_sort_value(row.get("Size")),
                )
            )

        cur.executemany(
            """
            INSERT OR REPLACE INTO colors(profile, kod, nazwa_pl, nazwa_en)
            VALUES (?, ?, ?, ?)
            """,
            color_rows,
        )
        cur.executemany(
            """
            INSERT OR REPLACE INTO product_types(profile, kod, nazwa_pl, nazwa_en)
            VALUES (?, ?, ?, ?)
            """,
            type_rows,
        )
        cur.executemany(
            """
            INSERT INTO sizes(profile, rodzaj, size_value, eu, uk, us, fr, it, sort_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            size_rows,
        )

        conn.commit()
        return {
            "colors": len(color_rows),
            "types": len(type_rows),
            "sizes": len(size_rows),
        }
    finally:
        conn.close()


def _table_counts(profile: str, db_path: Optional[Path] = None) -> Dict[str, int]:
    ensure_schema(db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        cur = conn.cursor()
        counts = {}
        for table, key in (("colors", "colors"), ("product_types", "types"), ("sizes", "sizes")):
            cur.execute(f"SELECT COUNT(*) AS c FROM {table} WHERE profile = ?", (pkey,))
            counts[key] = int(cur.fetchone()["c"])
        return counts
    finally:
        conn.close()


def ensure_profile_seeded(profile: str, db_path: Optional[Path] = None) -> Dict[str, int]:
    counts = _table_counts(profile, db_path)
    if min(counts.values()) > 0:
        return counts
    return import_profile_from_xlsx(profile, replace_existing=True, db_path=db_path)


def list_colors(profile: str, db_path: Optional[Path] = None) -> List[Dict[str, str]]:
    ensure_profile_seeded(profile, db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT kod, nazwa_pl, nazwa_en
            FROM colors
            WHERE profile = ?
            ORDER BY kod
            """,
            (pkey,),
        ).fetchall()
        return [{"kod": r["kod"], "pl": r["nazwa_pl"], "en": r["nazwa_en"] or ""} for r in rows]
    finally:
        conn.close()


def upsert_color(profile: str, kod: str, pl: str, en: str, db_path: Optional[Path] = None) -> None:
    ensure_schema(db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO colors(profile, kod, nazwa_pl, nazwa_en)
            VALUES (?, ?, ?, ?)
            """,
            (pkey, _to_text(kod), _to_text(pl), _to_text(en)),
        )
        conn.commit()
    finally:
        conn.close()


def delete_color(profile: str, kod: str, db_path: Optional[Path] = None) -> None:
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        conn.execute("DELETE FROM colors WHERE profile = ? AND kod = ?", (pkey, _to_text(kod)))
        conn.commit()
    finally:
        conn.close()


def list_types(profile: str, db_path: Optional[Path] = None) -> List[Dict[str, str]]:
    ensure_profile_seeded(profile, db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT kod, nazwa_pl, nazwa_en
            FROM product_types
            WHERE profile = ?
            ORDER BY kod
            """,
            (pkey,),
        ).fetchall()
        return [{"kod": r["kod"], "pl": r["nazwa_pl"], "en": r["nazwa_en"] or ""} for r in rows]
    finally:
        conn.close()


def upsert_type(profile: str, kod: str, pl: str, en: str, db_path: Optional[Path] = None) -> None:
    ensure_schema(db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO product_types(profile, kod, nazwa_pl, nazwa_en)
            VALUES (?, ?, ?, ?)
            """,
            (pkey, _to_text(kod), _to_text(pl), _to_text(en)),
        )
        conn.commit()
    finally:
        conn.close()


def delete_type(profile: str, kod: str, db_path: Optional[Path] = None) -> None:
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        conn.execute("DELETE FROM product_types WHERE profile = ? AND kod = ?", (pkey, _to_text(kod)))
        conn.commit()
    finally:
        conn.close()


def list_sizes(profile: str, db_path: Optional[Path] = None) -> List[Dict[str, str]]:
    ensure_profile_seeded(profile, db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, rodzaj, size_value, eu, uk, us, fr, it
            FROM sizes
            WHERE profile = ?
            ORDER BY rodzaj, COALESCE(sort_value, 999999), size_value, id
            """,
            (pkey,),
        ).fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "id": str(r["id"]),
                    "rodzaj": r["rodzaj"],
                    "size": r["size_value"],
                    "eu": r["eu"] or "",
                    "uk": r["uk"] or "",
                    "us": r["us"] or "",
                    "fr": r["fr"] or "",
                    "it": r["it"] or "",
                }
            )
        return out
    finally:
        conn.close()


def upsert_size(
    profile: str,
    rodzaj: str,
    size: str,
    eu: str,
    uk: str,
    us: str,
    fr: str,
    it: str,
    row_id: str = "",
    db_path: Optional[Path] = None,
) -> None:
    ensure_schema(db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        if row_id:
            conn.execute(
                """
                UPDATE sizes
                SET rodzaj = ?, size_value = ?, eu = ?, uk = ?, us = ?, fr = ?, it = ?, sort_value = ?
                WHERE id = ? AND profile = ?
                """,
                (
                    _to_text(rodzaj),
                    _to_text(size),
                    _to_text(eu),
                    _to_text(uk),
                    _to_text(us),
                    _to_text(fr),
                    _to_text(it),
                    _to_sort_value(size),
                    int(row_id),
                    pkey,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO sizes(profile, rodzaj, size_value, eu, uk, us, fr, it, sort_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pkey,
                    _to_text(rodzaj),
                    _to_text(size),
                    _to_text(eu),
                    _to_text(uk),
                    _to_text(us),
                    _to_text(fr),
                    _to_text(it),
                    _to_sort_value(size),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def delete_size(profile: str, row_id: str, db_path: Optional[Path] = None) -> None:
    if not row_id:
        return
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        conn.execute("DELETE FROM sizes WHERE id = ? AND profile = ?", (int(row_id), pkey))
        conn.commit()
    finally:
        conn.close()


def load_profile_dataframes(profile: str, db_path: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_profile_seeded(profile, db_path)
    pkey = normalize_profile(profile)
    conn = _connect(db_path)
    try:
        colors = pd.read_sql_query(
            """
            SELECT
                kod AS KOD_KOLOR,
                nazwa_pl AS NAZWA_POLSKA_KOLOR,
                nazwa_en AS NAZWA_ANGIELSKA_KOLOR
            FROM colors
            WHERE profile = ?
            ORDER BY kod
            """,
            conn,
            params=(pkey,),
        )
        types = pd.read_sql_query(
            """
            SELECT
                kod AS KOD_RODZAJE,
                nazwa_pl AS NAZWA_POLSKA_RODZAJE,
                nazwa_en AS NAZWA_ANGIELSKA_RODZAJE
            FROM product_types
            WHERE profile = ?
            ORDER BY kod
            """,
            conn,
            params=(pkey,),
        )
        sizes = pd.read_sql_query(
            """
            SELECT
                rodzaj AS Rodzaj,
                size_value AS Size,
                eu AS EU,
                uk AS UK,
                us AS US,
                fr AS FR,
                it AS IT
            FROM sizes
            WHERE profile = ?
            ORDER BY rodzaj, COALESCE(sort_value, 999999), size_value, id
            """,
            conn,
            params=(pkey,),
        )
        return colors, types, sizes
    finally:
        conn.close()


def init_all_profiles_from_xlsx(db_path: Optional[Path] = None) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for profile in ("buty", "torby_paski", "ubrania"):
        out[profile] = ensure_profile_seeded(profile, db_path)
    return out
