"""Testy silnika wyceny.

Testy korzystają z uproszczonego cennika z okrągłymi stawkami,
żeby każdy wynik dało się sprawdzić ręcznie na kartce.
"""

import pytest

from wycena.pricing import (
    Zlecenie,
    cena_arkusza_papieru,
    czy_dwustronny,
    liczba_arkuszy,
    stawka_druku,
    wycen,
    z_naddatkiem,
)


@pytest.fixture
def cennik_testowy() -> dict:
    """Prosty cennik do testów: bez naddatku, marża 20%, VAT 23%."""
    return {
        "marza_procent": 20,
        "vat_procent": 23,
        "naddatek_procent": 0,
        "przygotowanie_zlecenia": 30.0,
        "kurs_eur_awaryjny": 4.0,
        "sklad_za_strone": 10.0,
        "uzytki_na_arkuszu": {"A4": 2, "A5": 4},
        "papiery": {
            "kreda": {"cena_arkusza": 0.50, "waluta": "PLN"},
            "premium": {"cena_arkusza": 0.10, "waluta": "EUR"},
        },
        "druk_za_arkusz": [{"od_arkuszy": 1, "4+4": 2.00, "4+0": 1.00}],
        "oprawy_za_egzemplarz": {"brak": 0.0, "zszywka": 0.20},
        "uszlachetnienia": {
            "brak": {"za_arkusz": 0.0, "przygotowanie": 0.0},
            "folia": {"za_arkusz": 1.00, "przygotowanie": 0.0},
        },
    }


# Funkcje pomocnicze


def test_czy_dwustronny():
    assert czy_dwustronny("4+4") is True
    assert czy_dwustronny("1+1") is True
    assert czy_dwustronny("4+0") is False


def test_liczba_arkuszy_ulotka():
    # 500 ulotek A5, 2 strony; na arkuszu 4 użytki z każdej strony, czyli 8 stron.
    # 500 * 2 / 8 = 125 arkuszy
    assert liczba_arkuszy(500, 2, 4, True) == 125


def test_liczba_arkuszy_katalog():
    # 100 katalogów A4 po 8 stron; arkusz mieści 2 * 2 = 4 strony.
    # 100 * 8 / 4 = 200 arkuszy
    assert liczba_arkuszy(100, 8, 2, True) == 200


def test_liczba_arkuszy_zaokragla_w_gore():
    # 3 ulotki A5: 3 * 2 / 8 = 0,75, a nie da się wydrukować 3/4 arkusza.
    assert liczba_arkuszy(3, 2, 4, True) == 1


def test_naddatek():
    assert z_naddatkiem(100, 5) == 105
    # 101 * 1,05 = 106,05, więc w górę do 107
    assert z_naddatkiem(101, 5) == 107
    assert z_naddatkiem(100, 0) == 100


def test_progi_ilosciowe_druku():
    progi = [
        {"od_arkuszy": 1, "4+4": 3.00},
        {"od_arkuszy": 100, "4+4": 2.00},
        {"od_arkuszy": 500, "4+4": 1.00},
    ]
    assert stawka_druku(50, "4+4", progi) == 3.00
    assert stawka_druku(100, "4+4", progi) == 2.00  # granica progu należy do wyższego progu
    assert stawka_druku(499, "4+4", progi) == 2.00
    assert stawka_druku(2000, "4+4", progi) == 1.00


def test_przeliczenie_papieru_w_euro():
    papier = {"cena_arkusza": 0.10, "waluta": "EUR"}
    assert cena_arkusza_papieru(papier, 4.0) == pytest.approx(0.40)


# Pełne wyceny


def test_wycena_ulotki(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka", format="A5", liczba_stron=2, naklad=500, papier="kreda", kolor="4+4"
    )
    wynik = wycen(zlecenie, cennik_testowy)

    # arkusze: 125
    # papier: 125 * 0,50 = 62,50
    # druk: 125 * 2,00 + 30 = 280,00
    # skład: 2 * 10 = 20,00
    # koszt własny: 362,50; marża 20% = 72,50; netto 435,00
    # VAT 23% = 100,05; brutto 535,05; za sztukę netto 435 / 500 = 0,87
    assert wynik.arkusze == 125
    assert wynik.koszty["papier"] == 62.50
    assert wynik.koszty["druk"] == 280.00
    assert wynik.koszty["oprawa"] == 0.0
    assert wynik.koszty["uszlachetnienia"] == 0.0
    assert wynik.koszty["skład"] == 20.00
    assert wynik.koszt_wlasny == 362.50
    assert wynik.cena_netto == 435.00
    assert wynik.cena_brutto == 535.05
    assert wynik.cena_netto_za_sztuke == 0.87


def test_wycena_katalogu_z_oprawa_i_folia(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="katalog",
        format="A4",
        liczba_stron=8,
        naklad=100,
        papier="kreda",
        kolor="4+4",
        oprawa="zszywka",
        uszlachetnienie="folia",
    )
    wynik = wycen(zlecenie, cennik_testowy)

    # arkusze: 200; papier 100,00; druk 200 * 2 + 30 = 430,00
    # oprawa: 100 * 0,20 = 20,00
    # folia tylko na okładce: 100 * 4 / 4 = 100 arkuszy * 1,00 = 100,00
    # skład: 8 * 10 = 80,00
    # koszt własny 730,00; netto 876,00; brutto 1077,48
    assert wynik.koszty["oprawa"] == 20.00
    assert wynik.koszty["uszlachetnienia"] == 100.00
    assert wynik.koszt_wlasny == 730.00
    assert wynik.cena_netto == 876.00
    assert wynik.cena_brutto == 1077.48


def test_wycena_bez_skladu(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka",
        format="A5",
        liczba_stron=2,
        naklad=500,
        papier="kreda",
        kolor="4+4",
        sklad=False,
    )
    assert wycen(zlecenie, cennik_testowy).koszty["skład"] == 0.0


def test_wycena_uzywa_podanego_kursu_eur(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka", format="A5", liczba_stron=2, naklad=500, papier="premium", kolor="4+4"
    )
    # 125 arkuszy * 0,10 EUR * 5,00 PLN = 62,50
    wynik = wycen(zlecenie, cennik_testowy, kurs_eur=5.0)
    assert wynik.koszty["papier"] == 62.50


# Walidacja błędnych zleceń


def test_blad_druk_jednostronny_wielu_stron(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka", format="A5", liczba_stron=2, naklad=100, papier="kreda", kolor="4+0"
    )
    with pytest.raises(ValueError, match="jednostronny"):
        wycen(zlecenie, cennik_testowy)


def test_blad_oprawa_bez_wielokrotnosci_4(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="broszura",
        format="A5",
        liczba_stron=6,
        naklad=100,
        papier="kreda",
        kolor="4+4",
        oprawa="zszywka",
    )
    with pytest.raises(ValueError, match="wielokrotnością 4"):
        wycen(zlecenie, cennik_testowy)


def test_blad_zerowy_naklad(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka", format="A5", liczba_stron=2, naklad=0, papier="kreda", kolor="4+4"
    )
    with pytest.raises(ValueError, match="Nakład"):
        wycen(zlecenie, cennik_testowy)


def test_blad_nieznany_papier(cennik_testowy):
    zlecenie = Zlecenie(
        produkt="ulotka", format="A5", liczba_stron=2, naklad=100, papier="karton", kolor="4+4"
    )
    with pytest.raises(ValueError, match="papier"):
        wycen(zlecenie, cennik_testowy)
