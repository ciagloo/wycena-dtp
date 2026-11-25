"""Wykresy dla interfejsu: struktura kosztów i najczęściej wyceniane produkty.

Oba wykresy to poziome słupki posortowane od największej wartości,
w jednym kolorze, bo pokazują jedną serię danych.
"""

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from wycena.money import format_zl

KOLOR_SLUPKOW = "#257de0"


def _slupki_poziome(dane: pd.DataFrame, x: str, y: str, tytul: str) -> Figure:
    """Wspólny wygląd wykresów: poziome słupki z opisem wartości przy końcu słupka."""
    wykres = px.bar(dane, x=x, y=y, orientation="h", text="Opis", title=tytul)
    wykres.update_traces(
        marker_color=KOLOR_SLUPKOW,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{text}<extra></extra>",
    )
    wykres.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis={"showticklabels": False, "showgrid": False},
        margin={"l": 0, "r": 110, "t": 50, "b": 0},
        height=80 + 50 * len(dane),
        bargap=0.35,
    )
    return wykres


def wykres_kosztow(koszty: dict[str, float], koszt_wlasny: float) -> Figure:
    """Struktura kosztu własnego: kwota i udział każdej składowej większej od zera."""
    dane = pd.DataFrame(
        {"Składnik": [nazwa.capitalize() for nazwa in koszty], "Kwota": list(koszty.values())}
    )
    dane = dane[dane["Kwota"] > 0].sort_values("Kwota")
    udzialy = dane["Kwota"] / koszt_wlasny * 100
    dane["Opis"] = [
        f"{format_zl(k)} ({u:.0f}%)" for k, u in zip(dane["Kwota"], udzialy, strict=True)
    ]
    return _slupki_poziome(dane, "Kwota", "Składnik", "Struktura kosztu własnego")


def wykres_produktow(produkty: pd.Series) -> Figure:
    """Liczba wycen dla każdego rodzaju publikacji."""
    dane = pd.DataFrame({"Produkt": produkty.index, "Liczba": produkty.values})
    dane = dane.sort_values("Liczba")
    dane["Opis"] = dane["Liczba"].astype(str)
    return _slupki_poziome(dane, "Liczba", "Produkt", "Najczęściej wyceniane produkty")
