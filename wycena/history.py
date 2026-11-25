"""Zapis historii wycen w SQLite i proste statystyki.

SQLite to baza danych w jednym pliku (dane/historia.db), wbudowana w Pythona.
Nie wymaga instalowania serwera bazy danych.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from wycena.pricing import Wycena, Zlecenie

SCIEZKA_BAZY = Path(__file__).parent.parent / "dane" / "historia.db"

UTWORZ_TABELE = """
CREATE TABLE IF NOT EXISTS wyceny (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    klient TEXT,
    produkt TEXT NOT NULL,
    format TEXT NOT NULL,
    liczba_stron INTEGER NOT NULL,
    naklad INTEGER NOT NULL,
    papier TEXT NOT NULL,
    kolor TEXT NOT NULL,
    oprawa TEXT NOT NULL,
    uszlachetnienie TEXT NOT NULL,
    cena_netto REAL NOT NULL,
    cena_brutto REAL NOT NULL
)
"""


def _polacz(sciezka: Path) -> sqlite3.Connection:
    """Otwiera połączenie z bazą i tworzy tabelę, jeśli jeszcze nie istnieje."""
    polaczenie = sqlite3.connect(sciezka)
    polaczenie.execute(UTWORZ_TABELE)
    return polaczenie


def zapisz_wycene(
    zlecenie: Zlecenie,
    wynik: Wycena,
    klient: str = "",
    sciezka: Path = SCIEZKA_BAZY,
    teraz: datetime | None = None,
) -> None:
    """Dopisuje jedną wycenę do bazy."""
    if teraz is None:
        teraz = datetime.now()
    polaczenie = _polacz(sciezka)
    try:
        # Znaki ? to parametry zapytania. Baza sama bezpiecznie wstawia wartości,
        # co chroni przed atakiem SQL injection (np. złośliwą nazwą klienta).
        polaczenie.execute(
            """
            INSERT INTO wyceny (data, klient, produkt, format, liczba_stron, naklad, papier,
                                kolor, oprawa, uszlachetnienie, cena_netto, cena_brutto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                teraz.strftime("%Y-%m-%d %H:%M"),
                klient,
                zlecenie.produkt,
                zlecenie.format,
                zlecenie.liczba_stron,
                zlecenie.naklad,
                zlecenie.papier,
                zlecenie.kolor,
                zlecenie.oprawa,
                zlecenie.uszlachetnienie,
                wynik.cena_netto,
                wynik.cena_brutto,
            ),
        )
        polaczenie.commit()  # zatwierdza zapis w pliku bazy
    finally:
        polaczenie.close()  # zamyka połączenie także wtedy, gdy wystąpi błąd


def wczytaj_historie(sciezka: Path = SCIEZKA_BAZY) -> pd.DataFrame:
    """Zwraca wszystkie zapisane wyceny jako tabelę pandas, od najnowszej."""
    polaczenie = _polacz(sciezka)
    try:
        return pd.read_sql("SELECT * FROM wyceny ORDER BY id DESC", polaczenie)
    finally:
        polaczenie.close()


def statystyki(historia: pd.DataFrame) -> dict:
    """Liczy podstawowe statystyki z historii wycen."""
    if historia.empty:
        return {
            "liczba_wycen": 0,
            "srednia_netto": 0.0,
            "suma_netto": 0.0,
            "produkty": pd.Series(dtype=int),
        }
    return {
        "liczba_wycen": len(historia),
        "srednia_netto": round(historia["cena_netto"].mean(), 2),
        "suma_netto": round(historia["cena_netto"].sum(), 2),
        # value_counts liczy, ile razy wystąpił każdy produkt, od najczęstszego
        "produkty": historia["produkt"].value_counts(),
    }
