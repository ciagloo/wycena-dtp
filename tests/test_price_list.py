"""Testy wczytywania cennika i zgodności danych przykładowych z cennikiem."""

import json

import pytest

from wycena.price_list import SCIEZKA_CENNIKA, wczytaj_cennik
from wycena.pricing import Zlecenie, wycen


def test_cennik_wczytuje_sie():
    cennik = wczytaj_cennik()
    assert cennik["vat_procent"] == 23
    assert "kreda 130 g" in cennik["papiery"]


def test_brakujace_pole_w_cenniku(tmp_path):
    # tmp_path to tymczasowy folder tworzony przez pytest na czas testu.
    zly_plik = tmp_path / "cennik.json"
    zly_plik.write_text('{"vat_procent": 23}', encoding="utf-8")
    with pytest.raises(ValueError, match="brakuje"):
        wczytaj_cennik(zly_plik)


def test_wszystkie_przykladowe_zlecenia_da_sie_wycenic():
    cennik = wczytaj_cennik()
    sciezka = SCIEZKA_CENNIKA.parent / "przykladowe_zlecenia.json"
    with open(sciezka, encoding="utf-8") as plik:
        zlecenia = json.load(plik)

    for dane in zlecenia:
        # ** rozpakowuje słownik na argumenty, np. format="A5", naklad=500
        wynik = wycen(Zlecenie(**dane), cennik)
        assert wynik.cena_brutto > wynik.cena_netto > 0
