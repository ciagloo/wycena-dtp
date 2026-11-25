"""Testy wykresów: sprawdzamy dane na wykresie, nie jego wygląd."""

import pandas as pd

from wycena.charts import wykres_kosztow, wykres_produktow


def test_wykres_kosztow_pomija_zerowe_skladowe():
    koszty = {"papier": 50.0, "druk": 150.0, "oprawa": 0.0}
    wykres = wykres_kosztow(koszty, koszt_wlasny=200.0)
    slupki = list(wykres.data[0].y)
    assert "Oprawa" not in slupki
    # Słupki posortowane rosnąco, więc największy jest na górze wykresu.
    assert slupki == ["Papier", "Druk"]
    assert wykres.data[0].text[1] == "150,00 zł (75%)"


def test_wykres_produktow():
    produkty = pd.Series({"ulotka": 3, "katalog": 1})
    wykres = wykres_produktow(produkty)
    assert list(wykres.data[0].y) == ["katalog", "ulotka"]
