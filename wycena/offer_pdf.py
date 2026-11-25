"""Generowanie oferty PDF dla klienta.

Oferta pokazuje parametry zlecenia i cenę końcową.
Nie pokazuje kosztów wewnętrznych ani marży, bo to informacje tylko dla studia.
"""

from datetime import date, datetime, timedelta
from pathlib import Path

from fpdf import FPDF

from wycena.money import format_zl
from wycena.pricing import Wycena, Zlecenie

# Fira Sans (licencja OFL) obsługuje polskie znaki; wbudowane fonty PDF ich nie mają.
FOLDER_FONTOW = Path(__file__).parent.parent / "dane" / "fonty"

# Kolory w zapisie RGB
CZARNY = (25, 25, 25)
SZARY = (110, 110, 110)
LINIA = (205, 205, 205)


def numer_oferty(teraz: datetime) -> str:
    """Tworzy numer oferty z daty i godziny, np. OF/2026/11/25/1430."""
    return f"OF/{teraz:%Y/%m/%d/%H%M}"


def termin_waznosci(data_wystawienia: date, dni: int) -> date:
    """Zwraca datę, do której oferta jest ważna."""
    return data_wystawienia + timedelta(days=dni)


def zwiaz_spojniki(tekst: str) -> str:
    """Wstawia twardą spację po jednoliterowych spójnikach.

    Zasada polskiej typografii: spójniki i przyimki jednoliterowe (i, w, z, o, a)
    nie mogą zostać na końcu linii. Twarda spacja (\\u00a0) wiąże je z następnym słowem.
    """
    for spojnik in [" i ", " w ", " z ", " o ", " a "]:
        tekst = tekst.replace(spojnik, spojnik.rstrip() + "\u00a0")
    return tekst


def opis_zlecenia(zlecenie: Zlecenie) -> list[tuple[str, str]]:
    """Zamienia zlecenie na listę par (etykieta, wartość) do tabeli w ofercie."""
    return [
        ("Rodzaj publikacji", zlecenie.produkt),
        ("Format", zlecenie.format),
        ("Liczba stron", str(zlecenie.liczba_stron)),
        ("Nakład", f"{zlecenie.naklad} egz."),
        ("Papier", zlecenie.papier),
        ("Kolor druku", zlecenie.kolor),
        ("Oprawa", zlecenie.oprawa),
        ("Uszlachetnienie", zlecenie.uszlachetnienie),
        ("Skład", "w cenie" if zlecenie.sklad else "pliki do druku dostarcza klient"),
    ]


def _wiersz(pdf: FPDF, etykieta: str, wartosc: str, pogrubiony: bool = False) -> None:
    """Rysuje jeden wiersz tabeli: etykieta po lewej, wartość po prawej, cienka linia pod spodem."""
    styl = "B" if pogrubiony else ""
    pdf.set_font("Fira", "", 10)
    pdf.set_text_color(*SZARY)
    pdf.cell(70, 8, etykieta)
    pdf.set_font("Fira", styl, 10)
    pdf.set_text_color(*CZARNY)
    pdf.cell(0, 8, wartosc, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*LINIA)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())


def _naglowek_sekcji(pdf: FPDF, tytul: str) -> None:
    pdf.ln(8)
    pdf.set_font("Fira", "B", 12)
    pdf.set_text_color(*CZARNY)
    pdf.cell(0, 8, tytul, new_x="LMARGIN", new_y="NEXT")


def generuj_oferte(
    zlecenie: Zlecenie,
    wynik: Wycena,
    studio: dict,
    vat_procent: float,
    dni_waznosci: int,
    klient: str = "",
    teraz: datetime | None = None,
) -> bytes:
    """Tworzy ofertę PDF i zwraca ją jako bajty, gotowe do pobrania lub zapisu do pliku.

    teraz: data wystawienia; w testach podajemy stałą datę, żeby wynik był powtarzalny.
    """
    if teraz is None:
        teraz = datetime.now()
    wazna_do = termin_waznosci(teraz.date(), dni_waznosci)

    pdf = FPDF(format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.add_font("Fira", "", FOLDER_FONTOW / "FiraSans-Regular.ttf")
    pdf.add_font("Fira", "B", FOLDER_FONTOW / "FiraSans-SemiBold.ttf")
    pdf.add_page()

    # Nagłówek: dane studia po lewej, numer i data po prawej.
    pdf.set_font("Fira", "B", 16)
    pdf.set_text_color(*CZARNY)
    pdf.cell(100, 9, studio["nazwa"])
    pdf.cell(0, 9, "Oferta", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Fira", "", 9)
    pdf.set_text_color(*SZARY)
    pdf.cell(100, 5, studio["adres"])
    pdf.cell(0, 5, f"Nr {numer_oferty(teraz)}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 5, f"{studio['email']}, tel. {studio['telefon']}")
    pdf.cell(0, 5, f"Data: {teraz:%d.%m.%Y}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_draw_color(*CZARNY)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())

    if klient:
        pdf.ln(6)
        pdf.set_font("Fira", "", 10)
        pdf.set_text_color(*SZARY)
        pdf.cell(20, 6, "Dla:")
        pdf.set_text_color(*CZARNY)
        pdf.set_font("Fira", "B", 10)
        pdf.cell(0, 6, klient, new_x="LMARGIN", new_y="NEXT")

    # Parametry zlecenia
    _naglowek_sekcji(pdf, "Przedmiot oferty")
    for etykieta, wartosc in opis_zlecenia(zlecenie):
        _wiersz(pdf, etykieta, wartosc)

    # Cena
    _naglowek_sekcji(pdf, "Cena")
    _wiersz(pdf, "Cena netto", format_zl(wynik.cena_netto))
    _wiersz(pdf, f"VAT ({vat_procent:g}%)", format_zl(wynik.vat))
    _wiersz(pdf, "Cena brutto", format_zl(wynik.cena_brutto), pogrubiony=True)
    _wiersz(pdf, "Cena za sztukę netto", format_zl(wynik.cena_netto_za_sztuke))
    _wiersz(pdf, "Cena za sztukę brutto", format_zl(wynik.cena_brutto_za_sztuke))

    # Warunki
    _naglowek_sekcji(pdf, "Warunki")
    pdf.set_font("Fira", "", 10)
    pdf.set_text_color(*CZARNY)
    warunki = (
        f"Oferta jest ważna do {wazna_do:%d.%m.%Y}. Ceny podano w złotych. "
        "Termin realizacji ustalamy po akceptacji oferty i plików do druku."
    )
    pdf.multi_cell(0, 6, zwiaz_spojniki(warunki), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
