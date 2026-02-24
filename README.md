# Etykiety

Projekt zawiera dwa niezalezne skrypty do generowania etykiet PDF na podstawie danych produktowych.

## Struktura
- `buty/etykiety_14.py` - generator etykiet dla asortymentu butowego.
- `Torby_paski/etykiety_13T3.py` - generator etykiet dla toreb, paskow i pozostalych grup.

Kazdy katalog zawiera:
- slowniki: `Kolory.xlsx`, `Rodzaje.xlsx`, `Rozmiary.xlsx`
- tlo etykiet: `1.png`, `2.png`, `3.png`
- przykladowe pliki danych (`.dbf`, `.xlsx`)

## Jak to dziala (stan bazowy 0.1.0)
1. Uzytkownik wybiera plik wejsciowy (`DBF` / `XLSX`) przez okno dialogowe.
2. Skrypt laduje slowniki z katalogu, w ktorym sam sie znajduje.
3. Tworzy etykiety PDF 60x50 mm.
4. Dla kazdej etykiety generuje kod kreskowy EAN13 i dokleja go do PDF.
5. Tymczasowe pliki `barcode_*.png` sa usuwane na koncu.

## Wymagania Python
- `pandas`
- `reportlab`
- `python-barcode`
- `Pillow` (zaleznosc writera obrazu)
- `dbfread`
- `openpyxl`

## Wersjonowanie
Aktualna wersja jest w pliku `VERSION`, historia zmian w `CHANGELOG.md`.
