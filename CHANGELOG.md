# Changelog

## [0.2.0] - 2026-02-24
### Added
- `etykiety_launcher.py` - jedno okno startowe do wyboru profilu: `Buty` lub `Torby i paski`.
- `buty/embedded_backgrounds.py` - osadzone tla etykiet (1/2/3) bez koniecznosci odczytu PNG z dysku.
- `Torby_paski/embedded_backgrounds.py` - osadzone tla etykiet (1/2/3) bez koniecznosci odczytu PNG z dysku.

### Changed
- `buty/etykiety_14.py`: rysowanie tla najpierw z zasobow osadzonych, z fallbackiem do pliku PNG.
- `Torby_paski/etykiety_13T3.py`: rysowanie tla najpierw z zasobow osadzonych, z fallbackiem do pliku PNG.
- Wyglad etykiety pozostaje nienaruszony (te same bitmapy tla, tylko zrodlo przeniesione do kodu).

## [0.1.0] - 2026-02-24
### Added
- Inicjalizacja repozytorium `etykiety` i wersjonowanie calego zestawu danych i skryptow.
- Plik `README.md` z opisem obecnej struktury i dzialania.
- Plik `VERSION` z numerem wersji.
- Plik `.gitignore` dla plikow tymczasowych (m.in. `barcode_*.png`).

### Baseline
- Dwa niezalezne generatory etykiet:
  - `buty/etykiety_14.py`
  - `Torby_paski/etykiety_13T3.py`
- Wejscie danych: `DBF` / `XLSX`.
- Slowniki: `Kolory.xlsx`, `Rodzaje.xlsx`, `Rozmiary.xlsx` (osobno dla obu katalogow).
- Tla etykiet: `1.png`, `2.png`, `3.png` (osobno dla obu katalogow).
