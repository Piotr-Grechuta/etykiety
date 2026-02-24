# Changelog

## [0.4.0] - 2026-02-24
### Added
- Nowy profil `ubrania` oparty o folder `ubrania`.
- Obsluga slownikow ubrań z plikow:
  - `ubrania/GRUPY TOWAROWE.xlsx` (sheet `Rodzaje`)
  - `ubrania/TABELA KOLORÓW.xlsx` (sheet `Kolory`)
  - `ubrania/TABELA ROZMIARÓW.xlsx` (sheet `Rozmiary`)
- Profil `Ubrania` w GUI startowym.
- Profil `ubrania` w GUI zarzadzania listami.

### Changed
- `dictionary_store.py`:
  - adapter nazw plikow slownikow per profil,
  - import/init dla trzech profili (`buty`, `torby_paski`, `ubrania`).
- `etykiety_launcher.py`:
  - uruchamianie generatora z przekazaniem profilu przez `ETYKIETY_PROFILE`.
- `Torby_paski/etykiety_13T3.py`:
  - ladowanie slownikow wg `ETYKIETY_PROFILE` (dzieki temu obsluguje tez `ubrania`),
  - rozszerzone parametry czcionki rozmiaru dla typow odziezowych.
- `buty/etykiety_14.py`:
  - ujednolicone ladowanie profilu z `ETYKIETY_PROFILE`.

## [0.3.0] - 2026-02-24
### Added
- `dictionary_store.py`: centralna obsluga slownikow w SQLite (`etykiety_slowniki.db`).
- `dictionary_manager_gui.py`: GUI list/slownikow (Kolory, Rodzaje, Rozmiary) z CRUD.
- Automatyczne zasilenie bazy SQLite danymi z istniejących arkuszy XLSX.
- Przycisk `Zarzadzaj listami` w launcherze.

### Changed
- `buty/etykiety_14.py`: slowniki sa ladowane z SQLite przez `dictionary_store`.
- `Torby_paski/etykiety_13T3.py`: slowniki sa ladowane z SQLite przez `dictionary_store`.
- `etykiety_launcher.py`: integracja uruchamiania generatora z inicjalizacja slownikow i GUI list.
- Rozmiary w SQLite sa przechowywane z `id`, aby zachowac wszystkie rekordy z XLSX 1:1.

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
