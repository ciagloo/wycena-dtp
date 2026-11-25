"""Testy generowania oferty PDF."""

from datetime import date, datetime

from wycena.offer_pdf import (
    generuj_oferte,
    numer_oferty,
    opis_zlecenia,
    termin_waznosci,
    zwiaz_spojniki,
)
from wycena.price_list import wczytaj_cennik
from wycena.pricing import Zlecenie, wycen

ZLECENIE = Zlecenie(
    produkt="ulotka", format="A5", liczba_stron=2, naklad=500, papier="kreda 130 g", kolor="4+4"
)


def test_numer_oferty():
    assert numer_oferty(datetime(2026, 11, 25, 14, 30)) == "OF/2026/11/25/1430"


def test_termin_waznosci_przechodzi_na_kolejny_miesiac():
    assert termin_waznosci(date(2026, 11, 25), 14) == date(2026, 12, 9)


def test_twarda_spacja_po_spojniku():
    assert zwiaz_spojniki("oferty i plików") == "oferty i\u00a0plików"
    assert zwiaz_spojniki("druk w studiu") == "druk w\u00a0studiu"


def test_opis_zlecenia_bez_skladu():
    zlecenie = Zlecenie(
        produkt="ulotka",
        format="A5",
        liczba_stron=2,
        naklad=500,
        papier="kreda 130 g",
        kolor="4+4",
        sklad=False,
    )
    opis = dict(opis_zlecenia(zlecenie))
    assert opis["Nakład"] == "500 egz."
    assert opis["Skład"] == "pliki do druku dostarcza klient"


def test_generuje_poprawny_plik_pdf():
    cennik = wczytaj_cennik()
    wynik = wycen(ZLECENIE, cennik)
    pdf = generuj_oferte(
        ZLECENIE,
        wynik,
        studio=cennik["studio"],
        vat_procent=cennik["vat_procent"],
        dni_waznosci=cennik["waznosc_oferty_dni"],
        klient="Piekarnia Żółty Kłos",
        teraz=datetime(2026, 11, 25, 14, 30),
    )
    # Każdy plik PDF zaczyna się od znacznika %PDF.
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
