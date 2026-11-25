"""Testy historii wycen. Każdy test używa osobnej, tymczasowej bazy (tmp_path)."""

from datetime import datetime

import pandas as pd

from wycena.history import statystyki, wczytaj_historie, zapisz_wycene
from wycena.pricing import Wycena, Zlecenie


def _zlecenie(produkt: str) -> Zlecenie:
    return Zlecenie(
        produkt=produkt, format="A5", liczba_stron=2, naklad=100, papier="kreda", kolor="4+4"
    )


def _wynik(netto: float) -> Wycena:
    # Do historii trafiają tylko ceny końcowe, więc pozostałe pola mogą być zerami.
    return Wycena(
        arkusze=0,
        koszty={},
        koszt_wlasny=0.0,
        marza=0.0,
        cena_netto=netto,
        vat=0.0,
        cena_brutto=round(netto * 1.23, 2),
        cena_netto_za_sztuke=0.0,
        cena_brutto_za_sztuke=0.0,
    )


def test_pusta_historia(tmp_path):
    historia = wczytaj_historie(tmp_path / "test.db")
    assert historia.empty
    assert statystyki(historia)["liczba_wycen"] == 0


def test_zapis_i_odczyt(tmp_path):
    baza = tmp_path / "test.db"
    zapisz_wycene(
        _zlecenie("ulotka"),
        _wynik(100.0),
        klient="Firma A",
        sciezka=baza,
        teraz=datetime(2026, 11, 25, 10, 0),
    )
    historia = wczytaj_historie(baza)
    assert len(historia) == 1
    assert historia.loc[0, "klient"] == "Firma A"
    assert historia.loc[0, "data"] == "2026-11-25 10:00"
    assert historia.loc[0, "cena_brutto"] == 123.0


def test_najnowsza_wycena_jest_pierwsza(tmp_path):
    baza = tmp_path / "test.db"
    zapisz_wycene(_zlecenie("ulotka"), _wynik(100.0), sciezka=baza)
    zapisz_wycene(_zlecenie("katalog"), _wynik(500.0), sciezka=baza)
    assert wczytaj_historie(baza).loc[0, "produkt"] == "katalog"


def test_statystyki():
    historia = pd.DataFrame(
        {
            "produkt": ["ulotka", "ulotka", "katalog"],
            "cena_netto": [100.0, 200.0, 600.0],
        }
    )
    wynik = statystyki(historia)
    assert wynik["liczba_wycen"] == 3
    assert wynik["srednia_netto"] == 300.0  # (100 + 200 + 600) / 3
    assert wynik["suma_netto"] == 900.0
    assert wynik["produkty"]["ulotka"] == 2
    assert wynik["produkty"].index[0] == "ulotka"  # najczęstszy produkt jest pierwszy
