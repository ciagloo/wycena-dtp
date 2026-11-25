"""Pobranie kursu EUR z API Narodowego Banku Polskiego.

API NBP jest publiczne i bezpłatne. Zwraca kurs średni z tabeli A w formacie JSON.
Gdy API nie odpowiada (np. brak internetu), aplikacja używa kursu awaryjnego z cennika.
"""

from dataclasses import dataclass

import requests

ADRES_API = "https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"


@dataclass
class KursEur:
    """Kurs euro wraz z informacją, skąd pochodzi."""

    wartosc: float
    data: str  # data notowania NBP, np. "2026-11-24"; pusta dla kursu awaryjnego
    zrodlo: str  # "NBP" albo "cennik"


def odczytaj_kurs(odpowiedz: dict) -> KursEur:
    """Wyciąga kurs z odpowiedzi API.

    Przykład odpowiedzi: {"code": "EUR", "rates": [{"effectiveDate": "2026-11-24", "mid": 4.4633}]}
    """
    notowanie = odpowiedz["rates"][0]
    return KursEur(wartosc=notowanie["mid"], data=notowanie["effectiveDate"], zrodlo="NBP")


def pobierz_kurs_eur(kurs_awaryjny: float, limit_czasu: float = 5.0) -> KursEur:
    """Pobiera aktualny kurs EUR. Przy jakimkolwiek problemie zwraca kurs awaryjny.

    limit_czasu: po ilu sekundach przestajemy czekać na odpowiedź, żeby aplikacja nie zawisła.
    """
    try:
        odpowiedz = requests.get(ADRES_API, timeout=limit_czasu)
        odpowiedz.raise_for_status()  # zgłasza błąd, gdy serwer odpowie np. kodem 404 lub 500
        return odczytaj_kurs(odpowiedz.json())
    except (requests.RequestException, KeyError, IndexError, ValueError):
        # RequestException: brak połączenia, przekroczony czas, błąd serwera;
        # KeyError, IndexError, ValueError: odpowiedź w nieoczekiwanym formacie.
        return KursEur(wartosc=kurs_awaryjny, data="", zrodlo="cennik")
