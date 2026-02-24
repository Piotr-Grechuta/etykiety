# Etykiety

Projekt zawiera generatory etykiet PDF dla trzech profili towarowych:
- `buty`
- `torby_paski`
- `ubrania`

oraz jedno okno startowe do wyboru profilu i zarzadzania slownikami.

## Struktura
- `etykiety_launcher.py` - GUI startowe (wybor profilu, uruchomienie generatora, zarzadzanie listami).
- `dictionary_store.py` - baza SQLite slownikow + import z XLSX.
- `dictionary_manager_gui.py` - GUI do edycji list slownikowych.
- `buty/etykiety_14.py` - generator etykiet dla profilu butowego.
- `Torby_paski/etykiety_13T3.py` - generator etykiet dla profilu torby/paski oraz ubrania.

## Slowniki (od 0.4.0)
Slowniki sa trzymane w `etykiety_slowniki.db`.

### Profile i zrodla XLSX
- `buty`:
  - `buty/Kolory.xlsx` (Kolory)
  - `buty/Rodzaje.xlsx` (Rodzaje)
  - `buty/Rozmiary.xlsx` (Rozmiary)
- `torby_paski`:
  - `Torby_paski/Kolory.xlsx` (Kolory)
  - `Torby_paski/Rodzaje.xlsx` (Rodzaje)
  - `Torby_paski/Rozmiary.xlsx` (Rozmiary)
- `ubrania`:
  - `ubrania/TABELA KOLORÓW.xlsx` (Kolory)
  - `ubrania/GRUPY TOWAROWE.xlsx` (Rodzaje)
  - `ubrania/TABELA ROZMIARÓW.xlsx` (Rozmiary)

W GUI (`Zarzadzaj listami`) mozna:
- przegladac listy,
- dodawac/edytowac/usuwac rekordy,
- ponownie zaimportowac dane z XLSX dla wybranego profilu.

## Jak to dziala
1. Uzytkownik uruchamia `etykiety_launcher.py`.
2. Wybiera profil (`Buty`, `Torby i paski`, `Ubrania`).
3. Uruchamia generator i wskazuje plik danych (`DBF` / `XLSX`).
4. Generator laduje slowniki z SQLite.
5. Etykieta PDF 60x50 mm jest skladana z danymi i kodem EAN13.
6. Tlo etykiety jest rysowane z osadzonych zasobow (fallback do lokalnych PNG).

## Wymagania Python
- `pandas`
- `reportlab`
- `python-barcode`
- `Pillow`
- `dbfread`
- `openpyxl`

## Wersjonowanie
- aktualna wersja: `VERSION`
- historia zmian: `CHANGELOG.md`
