import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from barcode import EAN13
from barcode.writer import ImageWriter
import glob
import tkinter as tk
from tkinter import filedialog
from dbfread import DBF
from embedded_backgrounds import get_background_reader, has_background

# Parametry kodu kreskowego
barcode_width = 60 * mm
barcode_height = 15 * mm
barcode_x = 0 * mm  # Pozycja X kodu kreskowego
barcode_y = 35 * mm  # Pozycja Y kodu kreskowego

# Parametry SKU
sku_x = 3 * mm  # Pozycja X SKU
sku_y = barcode_y - 29 * mm  # Pozycja Y SKU - nad kodem kreskowym
sku_font_size = 16  # Wielkość czcionki SKU
sku_font = "Helvetica-Bold"  # Pogrubiona czcionka SKU

# Parametry dla polskiego rodzaju
nazwa_polska_rodzaje_font_size = 10  # Wielkość czcionki dla NAZWA_POLSKA_RODZAJE
nazwa_polska_rodzaje_font = "Helvetica-Bold"  # Pogrubiona czcionka dla NAZWA_POLSKA_RODZAJE
nazwa_polska_rodzaje_y = 32 * mm  # Pozycja Y dla NAZWA_POLSKA_RODZAJE

# Parametry dla angielskiego rodzaju
nazwa_angielska_rodzaje_font_size = 8  # Wielkość czcionki dla NAZWA_ANGIELSKA_RODZAJE
nazwa_angielska_rodzaje_font = "Helvetica"  # Czcionka dla NAZWA_ANGIELSKA_RODZAJE
nazwa_angielska_rodzaje_y = 29 * mm  # Pozycja Y dla NAZWA_ANGIELSKA_RODZAJE

# Parametry dla Kolory_razem
kolory_razem_font_size = 12  # Wielkość czcionki dla Kolory_razem
kolory_razem_font = "Helvetica-Bold"  # Pogrubiona czcionka dla Kolory_razem
kolory_razem_y = 23 * mm  # Pozycja Y dla Kolory_razem

# Domyślne parametry dla rozmiarów
eu_font_size = 22  # Wielkość czcionki dla rozmiaru EU (domyślna)
eu_x = 14 * mm  # Pozycja X dla rozmiaru EU (domyślna)
eu_y = 13 * mm  # Pozycja Y dla rozmiaru EU (domyślna)
eu_font = "Helvetica-Bold"  # Czcionka dla rozmiaru EU (domyślna)

# Parametry dla rozmiarów w zależności od rodzaju produktu
size_font_parameters = {
    'obuwie damskie': {
        'font_size': 22,
        'x': 14 * mm,
        'y': 13 * mm,
        'font': 'Helvetica-Bold',
    },
    'obuwie męskie': {
        'font_size': 24,
        'x': 12 * mm,
        'y': 15 * mm,
        'font': 'Helvetica-Bold',
    },
    'rękawiczki': {
        'font_size': 7,
        'x': 15 * mm,
        'y': 18 * mm,
        'font': 'Helvetica-Bold',
    },
    'kurtka': {
        'font_size': 20,
        'x': 7 * mm,
        'y': 16 * mm,
        'font': 'Helvetica-Bold',
    },
    'pasek': {
        'font_size': 16,
        'x': 7 * mm,
        'y': 15 * mm,
        'font': 'Helvetica-Bold',
    },
}

# Parametry dla pozostałych rozmiarów (UK, US, FR, IT)
uk_x = 40 * mm  # Pozycja X dla rozmiaru UK
uk_y = 17 * mm  # Pozycja Y dla rozmiaru UK
uk_font_size = 7  # Wielkość czcionki dla rozmiaru UK
uk_font = "Helvetica-Bold"  # Czcionka dla rozmiaru UK

us_x = 49 * mm  # Pozycja X dla rozmiaru US
us_y = 17 * mm  # Pozycja Y dla rozmiaru US
us_font_size = 7  # Wielkość czcionki dla rozmiaru US
us_font = "Helvetica-Bold"  # Czcionka dla rozmiaru US

fr_x = 40 * mm  # Pozycja X dla rozmiaru FR
fr_y = 13 * mm  # Pozycja Y dla rozmiaru FR
fr_font_size = 7  # Wielkość czcionki dla rozmiaru FR
fr_font = "Helvetica-Bold"  # Czcionka dla rozmiaru FR

it_x = 49 * mm  # Pozycja X dla rozmiaru IT
it_y = 13 * mm  # Pozycja Y dla rozmiaru IT
it_font_size = 7  # Wielkość czcionki dla rozmiaru IT
it_font = "Helvetica-Bold"  # Czcionka dla rozmiaru IT

# Funkcja generująca kod kreskowy
def generate_barcode(ean, filename):
    try:
        ean_code = EAN13(ean, writer=ImageWriter())
        ean_code.save(filename)
        if os.path.exists(f"{filename}.png.png"):
            os.rename(f"{filename}.png.png", f"{filename}.png")
    except Exception as e:
        print(f"Błąd podczas generowania kodu kreskowego dla EAN {ean}: {e}")

# Funkcja do wyszukiwania rodzaju w pliku Rodzaje.xlsx
def find_type_values(product_type, rodzaje_df):
    try:
        row = rodzaje_df[rodzaje_df.iloc[:, 1].str.strip().str.lower() == product_type.strip().lower()]
        if not row.empty:
            typ_polski = row.iloc[0, 1]
            typ_angielski = row.iloc[0, 2]
            return typ_polski, typ_angielski
        return product_type, None
    except Exception as e:
        return product_type, None

# Funkcja do wyszukiwania wartości w pliku Kolory.xlsx
def find_color_values(kolor_polski, kolory_df):
    try:
        row = kolory_df[kolory_df.iloc[:, 1].str.strip() == kolor_polski]
        if not row.empty:
            kolor_en = row.iloc[0, 2]
            return kolor_polski, kolor_en
        return kolor_polski, None
    except Exception as e:
        print(f"Błąd podczas wyszukiwania koloru: {e}")
        return kolor_polski, None

# Funkcja safe_convert
def safe_convert(value):
    try:
        if pd.isna(value) or value == '':
            return ''
        val = float(value)
        return str(int(val)) if val.is_integer() else str(val)
    except (ValueError, TypeError):
        return str(value) if pd.notna(value) else ''

# Funkcja do wyszukiwania wartości w pliku Rozmiary.xlsx
def find_size_values(size_code, type_text, rozmiary_df):
    try:
        type_text_cleaned = type_text.strip().lower()
        rozmiary_df['Rodzaj_cleaned'] = rozmiary_df['Rodzaj'].str.strip().str.lower()
        rozmiary_df['Size_str'] = rozmiary_df['Size'].astype(str).str.strip()

        row = rozmiary_df[
            (rozmiary_df['Size_str'] == str(size_code)) &
            (rozmiary_df['Rodzaj_cleaned'] == type_text_cleaned)
        ]

        if not row.empty:
            rozmiar_size = row.iloc[0]['Size']
            rozmiar_eu = row.iloc[0]['EU']
            rozmiar_uk = row.iloc[0]['UK']
            rozmiar_us = row.iloc[0]['US']
            rozmiar_fr = row.iloc[0]['FR']
            rozmiar_it = row.iloc[0]['IT']
            return rozmiar_size, rozmiar_eu, rozmiar_uk, rozmiar_us, rozmiar_fr, rozmiar_it
        return None, None, None, None, None, None
    except Exception as e:
        print(f"Błąd podczas wyszukiwania rozmiaru: {e}")
        return None, None, None, None, None, None

# Funkcja do tworzenia etykiet
def create_labels(data, kolory_df, rodzaje_df, rozmiary_df, output_pdf):
    total_labels_created = 0
    sku_group_count = {}
    total_rows_processed = len(data)
    try:
        c = None

        for index, row in data.iterrows():
            # Pobierz wartość z kolumny, która wskazuje, ile razy utworzyć etykietę
            label_count = int(row.iloc[9])  # Zastąp 9 indeksem kolumny z ilością etykiet

            total_labels_created += label_count  # Zsumowanie etykiet
            sku_data = str(row.iloc[2])  # Zastąp 2 indeksem kolumny z SKU

            # Aktualizacja liczby etykiet zgrupowanych dla danego SKU
            if sku_data in sku_group_count:
                sku_group_count[sku_data] += label_count
            else:
                sku_group_count[sku_data] = label_count

            for _ in range(label_count):
                if c is None:
                    c = canvas.Canvas(output_pdf, pagesize=(60 * mm, 50 * mm))

                label_width = 60 * mm
                label_height = 50 * mm

                # Pobranie rodzaju z kolumny
                produkt_typ_data = str(row.iloc[6]).strip()  # Zastąp 6 indeksem kolumny z rodzajem

                # Wybór tła na podstawie rodzaju
                if produkt_typ_data.lower().startswith("obuwie"):
                    background_image = os.path.join(script_dir, "2.png")
                elif produkt_typ_data.lower().startswith(("kurtka", "pasek")):
                    background_image = os.path.join(script_dir, "3.png")
                else:
                    background_image = os.path.join(script_dir, "1.png")

                # Rysowanie tla: najpierw wersja osadzona (bez zaleznosci od plikow PNG),
                # potem fallback do pliku lokalnego.
                background_drawn = False
                template_name = os.path.basename(background_image)
                if has_background(template_name):
                    try:
                        c.drawImage(
                            get_background_reader(template_name),
                            0,
                            0,
                            width=label_width,
                            height=label_height,
                        )
                        background_drawn = True
                    except Exception as e:
                        print(f"Błąd podczas rysowania osadzonego tła {template_name}: {e}")

                if not background_drawn and os.path.exists(background_image):
                    c.drawImage(background_image, 0, 0, width=label_width, height=label_height)

                # Ekstrakcja i podział SKU z kolumny
                sku_data = str(row.iloc[2])  # Zastąp 2 indeksem kolumny z SKU
                print(f"SKU Data: {sku_data}")  # Debugowanie

                if '@' in sku_data:
                    sku_cleaned = sku_data.split('@')[0]  # Pobranie części przed @
                    size_code = sku_data.split('@')[1][:3].lstrip('0')  # Pobieranie rozmiaru z SKU
                    size_code = size_code.strip()
                else:
                    sku_cleaned = sku_data  # Jeśli nie ma @, używamy całego SKU
                    size_code = None

                # Wyświetlenie SKU bez rozmiaru na etykiecie
                sku_parts = sku_cleaned
                c.setFont(sku_font, sku_font_size)
                c.drawString(sku_x, sku_y, sku_parts)

                # Pobranie koloru po polsku z kolumny
                kolor_polski = str(row.iloc[7]).strip()  # Zastąp 7 indeksem kolumny z kolorem
                kolor_pl, kolor_en = find_color_values(kolor_polski, kolory_df)

                kolory_razem = f"{kolor_pl} | {kolor_en}" if kolor_pl and kolor_en else "N/A"
                c.setFont(kolory_razem_font, kolory_razem_font_size)
                text_width = c.stringWidth(kolory_razem, kolory_razem_font, kolory_razem_font_size)
                kolory_razem_x = (label_width - text_width) / 2
                c.drawString(kolory_razem_x, kolory_razem_y, kolory_razem)

                # Pobranie rodzaju z kolumny (już pobrane wcześniej)
                typ_polski, typ_angielski = find_type_values(produkt_typ_data, rodzaje_df)

                # Umieszczanie polskiej wersji rodzaju na etykiecie
                if typ_polski:
                    c.setFont(nazwa_polska_rodzaje_font, nazwa_polska_rodzaje_font_size)
                    text_width_polski = c.stringWidth(typ_polski, nazwa_polska_rodzaje_font, nazwa_polska_rodzaje_font_size)
                    nazwa_polska_rodzaje_x = (label_width - text_width_polski) / 2
                    c.drawString(nazwa_polska_rodzaje_x, nazwa_polska_rodzaje_y, typ_polski)

                # Umieszczanie angielskiej wersji rodzaju na etykiecie
                if typ_angielski:
                    c.setFont(nazwa_angielska_rodzaje_font, nazwa_angielska_rodzaje_font_size)
                    text_width_angielski = c.stringWidth(typ_angielski, nazwa_angielska_rodzaje_font, nazwa_angielska_rodzaje_font_size)
                    nazwa_angielska_rodzaje_x = (label_width - text_width_angielski) / 2
                    c.drawString(nazwa_angielska_rodzaje_x, nazwa_angielska_rodzaje_y, typ_angielski)

                # Przetwarzanie produkt_typ_data do klucza dla parametrów rozmiaru
                produkt_typ_key = " ".join(produkt_typ_data.lower().split()[:2]).strip()  # Pobieramy 2 słowo jako klucz

                # Pobieranie parametrów czcionki rozmiaru w zależności od rodzaju produktu
                if produkt_typ_key in size_font_parameters:
                    size_params = size_font_parameters[produkt_typ_key]
                else:
                    # Użyj domyślnych parametrów
                    size_params = {
                        'font_size': eu_font_size,
                        'x': eu_x,
                        'y': eu_y,
                        'font': eu_font,
                    }

                # Pobranie rozmiarów z pliku Rozmiary.xlsx na podstawie size_code i produkt_typ
                if size_code:
                    print(f"Size code: {size_code}, Produkt Typ: {produkt_typ_data}")
                    rozmiar_size, rozmiar_eu, rozmiar_uk, rozmiar_us, rozmiar_fr, rozmiar_it = find_size_values(size_code, produkt_typ_data, rozmiary_df)

                    # Inicjalizacja flagi
                    size_displayed = False

                    # Wyświetlenie rozmiaru EU lub głównego rozmiaru
                    if pd.notna(rozmiar_eu) and rozmiar_eu != '':
                        size_text = f"EU: {safe_convert(rozmiar_eu)}"
                        size_displayed = True
                    elif pd.notna(rozmiar_size) and rozmiar_size != '':
                        size_text = f"Rozmiar: {safe_convert(rozmiar_size)}"
                        size_displayed = True
                    else:
                        size_text = ''

                    if size_displayed:
                        c.setFont(size_params['font'], size_params['font_size'])
                        c.drawString(size_params['x'], size_params['y'], size_text)
                    else:
                        print("Brak dostępnego rozmiaru do wyświetlenia.")

                    # Wyświetlenie pozostałych rozmiarów, jeśli są dostępne
                    # Możesz dostosować pozycje i czcionki dla pozostałych rozmiarów w zależności od potrzeb
                    if pd.notna(rozmiar_uk) and rozmiar_uk != '':
                        c.setFont(uk_font, uk_font_size)
                        c.drawString(uk_x, uk_y, f"UK: {safe_convert(rozmiar_uk)}")

                    if pd.notna(rozmiar_us) and rozmiar_us != '':
                        c.setFont(us_font, us_font_size)
                        c.drawString(us_x, us_y, f"US: {safe_convert(rozmiar_us)}")

                    if pd.notna(rozmiar_fr) and rozmiar_fr != '':
                        c.setFont(fr_font, fr_font_size)
                        c.drawString(fr_x, fr_y, f"FR: {safe_convert(rozmiar_fr)}")

                    if pd.notna(rozmiar_it) and rozmiar_it != '':
                        c.setFont(it_font, it_font_size)
                        c.drawString(it_x, it_y, f"IT: {safe_convert(rozmiar_it)}")
                else:
                    print("Brak size_code, pomijam rozmiary.")

                # Generowanie kodu kreskowego z kolumny EAN
                ean_code = str(row.iloc[5]).strip()  # Zastąp 5 indeksem kolumny z EAN
                barcode_file = os.path.join(os.getcwd(), f"barcode_{index}")
                generate_barcode(str(ean_code), barcode_file)

                barcode_image_path = f"{barcode_file}.png"
                if os.path.exists(barcode_image_path):
                    c.drawImage(barcode_image_path, barcode_x, barcode_y, width=barcode_width, height=barcode_height)

                c.showPage()

        if c:
            c.save()  # Zapisz plik PDF, jeśli jakieś etykiety zostały utworzone
            print(f"Etykiety zapisane do pliku {output_pdf}")

    except Exception as e:
        print(f"Błąd podczas tworzenia etykiet: {e}")

    # Informacja o przetworzonych wierszach, utworzonych etykietach i zgrupowanych SKU
    print(f"\nLiczba przetworzonych wierszy z pliku: {total_rows_processed}")
    print(f"Liczba utworzonych etykiet: {total_labels_created}")
    print("Liczba etykiet przypisanych do każdego SKU:")
    for sku, count in sku_group_count.items():
        print(f"SKU: {sku} - {count} etykiet")

    return total_rows_processed, total_labels_created, sku_group_count

# Funkcja do usuwania wygenerowanych plików z kodami kreskowymi
def cleanup_barcodes():
    barcode_files = glob.glob("barcode_*.png")
    for file in barcode_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Błąd podczas usuwania pliku {file}: {e}")

# Główna część programu
if __name__ == "__main__":
    # Inicjalizacja okna tkinter
    root = tk.Tk()
    root.withdraw()  # Ukrycie głównego okna

    # Otwarcie okna dialogowego do wyboru pliku (obsługa tylko Excel i DBF)
    input_file_path = filedialog.askopenfilename(
        title="Wybierz plik z danymi etykiet (Excel lub DBF)",
        filetypes=[("Pliki danych", "*.xlsx *.xls *.dbf"), ("Wszystkie pliki", "*.*")]
    )

    # Wygenerowanie nazwy pliku PDF na podstawie nazwy pliku wejściowego
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_pdf = f"{base_name}.pdf"

    # Określenie rozszerzenia pliku
    file_extension = os.path.splitext(input_file_path)[1].lower()

    # Wczytanie danych z wybranego pliku (Excel lub DBF)
    if file_extension in ['.xlsx', '.xls']:
        # Wczytanie pliku Excel
        etykieta_data = pd.read_excel(input_file_path, header=None)
    elif file_extension == '.dbf':
        # Wczytanie pliku DBF
        dbf_table = DBF(input_file_path, load=True, encoding='cp1250')  # Ustaw odpowiednie kodowanie
        # Konwersja do DataFrame pandas
        etykieta_data = pd.DataFrame(iter(dbf_table))
        # Resetowanie indeksów kolumn do liczb całkowitych
        etykieta_data.columns = range(etykieta_data.shape[1])
    else:
        print("Nieobsługiwany format pliku.")
        exit()

    # Sprawdzenie, czy dane zostały wczytane
    print("Dane etykiet:")
    print(etykieta_data.head())

    # Określenie ścieżki do folderu, w którym znajduje się skrypt
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Konstrukcja pełnych ścieżek do plików pomocniczych
    kolory_path = os.path.join(script_dir, 'Kolory.xlsx')
    rodzaje_path = os.path.join(script_dir, 'Rodzaje.xlsx')
    rozmiary_path = os.path.join(script_dir, 'Rozmiary.xlsx')

    # Wczytanie danych pomocniczych z plików Excel znajdujących się w bieżącym folderze
    kolory_data = pd.read_excel(kolory_path, sheet_name='Kolory')
    rodzaje_data = pd.read_excel(rodzaje_path, sheet_name='Rodzaje')
    rozmiary_data = pd.read_excel(rozmiary_path, sheet_name='Rozmiary')

    # Konwersja kolumn rozmiarów
    for col in ['EU', 'UK', 'US', 'FR', 'IT']:
        rozmiary_data[col] = rozmiary_data[col].apply(safe_convert)

    # Wywołanie funkcji z użyciem zdefiniowanych parametrów
    total_rows, total_labels, sku_group_count = create_labels(
        etykieta_data, kolory_data, rodzaje_data, rozmiary_data, output_pdf=output_pdf
    )

    # Usunięcie plików z kodami kreskowymi po utworzeniu PDF
    cleanup_barcodes()
