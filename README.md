# Etykiety

Projekt zawiera dwa generatory etykiet PDF na podstawie danych produktowych oraz jedno okno startowe do wyboru profilu.

## Struktura
- `etykiety_launcher.py` - uruchamiacz z wyborem profilu (`Buty` / `Torby i paski`).
- `buty/etykiety_14.py` - generator etykiet dla asortymentu butowego.
- `Torby_paski/etykiety_13T3.py` - generator etykiet dla toreb, paskow i pozostalych grup.

Kazdy katalog (`buty`, `Torby_paski`) zawiera:
- slowniki: `Kolory.xlsx`, `Rodzaje.xlsx`, `Rozmiary.xlsx`
- osadzone tla etykiet w kodzie: `embedded_backgrounds.py`
- kompatybilne pliki tla PNG (`1.png`, `2.png`, `3.png`) jako fallback
- przykladowe pliki danych (`.dbf`, `.xlsx`)

## Jak to dziala (od 0.2.0)
1. Uzytkownik uruchamia `etykiety_launcher.py` i wybiera profil.
2. Generator otwiera okno wyboru pliku wejsciowego (`DBF` / `XLSX`).
3. Slowniki ladowane sa z katalogu danego profilu.
4. Etykieta PDF 60x50 mm jest skladana z danymi i kodem EAN13.
5. Tlo etykiety jest rysowane z zasobow osadzonych (bez zaleznosci od PNG na dysku).
6. Jesli osadzone tlo nie moze byc wczytane, generator uzywa PNG jako fallback.

## Wymagania Python
- `pandas`
- `reportlab`
- `python-barcode`
- `Pillow` (zaleznosc writera obrazu)
- `dbfread`
- `openpyxl`

## Wersjonowanie
- aktualna wersja: `VERSION`
- historia zmian: `CHANGELOG.md`
