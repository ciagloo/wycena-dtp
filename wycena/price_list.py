"""Wczytanie cennika z pliku dane/cennik.json.

Cennik jest w osobnym pliku, żeby można było zmienić stawki
bez zmiany kodu aplikacji.
"""

import json
from pathlib import Path

# Ścieżka liczona względem tego pliku, więc działa niezależnie od tego,
# z którego folderu uruchomimy aplikację.
SCIEZKA_CENNIKA = Path(__file__).parent.parent / "dane" / "cennik.json"

# Klucze, bez których silnik wyceny nie zadziała.
WYMAGANE_KLUCZE = [
    "marza_procent",
    "vat_procent",
    "naddatek_procent",
    "przygotowanie_zlecenia",
    "kurs_eur_awaryjny",
    "sklad_za_strone",
    "produkty",
    "uzytki_na_arkuszu",
    "papiery",
    "druk_za_arkusz",
    "oprawy_za_egzemplarz",
    "limity_stron_oprawy",
    "uszlachetnienia",
]


def wczytaj_cennik(sciezka: Path = SCIEZKA_CENNIKA) -> dict:
    """Wczytuje cennik z pliku JSON i sprawdza, czy ma wszystkie potrzebne pola."""
    with open(sciezka, encoding="utf-8") as plik:
        cennik = json.load(plik)

    brakujace = [klucz for klucz in WYMAGANE_KLUCZE if klucz not in cennik]
    if brakujace:
        raise ValueError(f"W cenniku brakuje pól: {', '.join(brakujace)}")

    return cennik
