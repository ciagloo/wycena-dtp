"""Testy pobierania kursu EUR.

Testy nie łączą się z prawdziwym API NBP. monkeypatch (narzędzie pytest) podmienia funkcję
requests.get na udawaną, więc testy działają bez internetu i zawsze dają ten sam wynik.
"""

import requests

from wycena import nbp

PRZYKLADOWA_ODPOWIEDZ = {
    "table": "A",
    "code": "EUR",
    "rates": [{"no": "228/A/NBP/2026", "effectiveDate": "2026-11-24", "mid": 4.4633}],
}


class UdawanaOdpowiedz:
    """Zachowuje się jak odpowiedź z requests, ale zwraca przygotowane dane."""

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return PRZYKLADOWA_ODPOWIEDZ


def test_odczytaj_kurs():
    kurs = nbp.odczytaj_kurs(PRZYKLADOWA_ODPOWIEDZ)
    assert kurs.wartosc == 4.4633
    assert kurs.data == "2026-11-24"
    assert kurs.zrodlo == "NBP"


def test_pobierz_kurs_z_api(monkeypatch):
    monkeypatch.setattr(nbp.requests, "get", lambda adres, timeout: UdawanaOdpowiedz())
    kurs = nbp.pobierz_kurs_eur(kurs_awaryjny=4.0)
    assert kurs.wartosc == 4.4633
    assert kurs.zrodlo == "NBP"


def test_kurs_awaryjny_gdy_brak_polaczenia(monkeypatch):
    def brak_internetu(adres, timeout):
        raise requests.ConnectionError("brak połączenia")

    monkeypatch.setattr(nbp.requests, "get", brak_internetu)
    kurs = nbp.pobierz_kurs_eur(kurs_awaryjny=4.0)
    assert kurs.wartosc == 4.0
    assert kurs.zrodlo == "cennik"


def test_kurs_awaryjny_gdy_zly_format_odpowiedzi(monkeypatch):
    class PustaOdpowiedz(UdawanaOdpowiedz):
        def json(self) -> dict:
            return {"rates": []}  # brak notowań, więc odczytaj_kurs zgłosi IndexError

    monkeypatch.setattr(nbp.requests, "get", lambda adres, timeout: PustaOdpowiedz())
    kurs = nbp.pobierz_kurs_eur(kurs_awaryjny=4.0)
    assert kurs.zrodlo == "cennik"
