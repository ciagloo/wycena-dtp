"""Silnik wyceny: liczy koszt papieru, druku, oprawy, uszlachetnień i składu.

Założenie technologiczne: druk cyfrowy na arkuszach SRA3 (320 x 450 mm),
typowy dla małych i średnich nakładów w studiu DTP.
"""

import math
from dataclasses import dataclass


@dataclass
class Zlecenie:
    """Parametry zlecenia wpisane przez użytkownika w formularzu."""

    produkt: str
    format: str
    liczba_stron: int
    naklad: int
    papier: str
    kolor: str
    oprawa: str = "brak"
    uszlachetnienie: str = "brak"
    sklad: bool = True  # czy studio wykonuje skład (projekt) publikacji


@dataclass
class Wycena:
    """Wynik wyceny: koszty składowe i ceny końcowe."""

    arkusze: int
    koszty: dict[str, float]
    koszt_wlasny: float
    marza: float
    cena_netto: float
    vat: float
    cena_brutto: float
    cena_netto_za_sztuke: float
    cena_brutto_za_sztuke: float


def czy_dwustronny(kolor: str) -> bool:
    """Druk jest dwustronny, gdy druga liczba w zapisie koloru nie jest zerem (4+4, 1+1)."""
    return not kolor.endswith("+0")


def liczba_arkuszy(naklad: int, liczba_stron: int, uzytki: int, dwustronny: bool) -> int:
    """Liczy, ile arkuszy SRA3 trzeba zadrukować.

    uzytki: ile stron danego formatu mieści się na jednej stronie arkusza.
    Przy druku dwustronnym arkusz mieści dwa razy więcej stron.
    Wynik zaokrąglamy w górę, bo nie da się wydrukować części arkusza.
    """
    strony_na_arkusz = uzytki * (2 if dwustronny else 1)
    return math.ceil(naklad * liczba_stron / strony_na_arkusz)


def z_naddatkiem(arkusze: int, naddatek_procent: float) -> int:
    """Dolicza naddatek technologiczny, czyli zapas arkuszy na próby i odpady."""
    return math.ceil(arkusze * (1 + naddatek_procent / 100))


def cena_arkusza_papieru(papier: dict, kurs_eur: float) -> float:
    """Zwraca cenę arkusza w PLN. Papiery wyceniane w euro przelicza po kursie."""
    if papier["waluta"] == "EUR":
        return papier["cena_arkusza"] * kurs_eur
    return papier["cena_arkusza"]


def stawka_druku(arkusze: int, kolor: str, progi: list[dict]) -> float:
    """Wybiera stawkę za arkusz według progów ilościowych.

    Progi są ułożone rosnąco. Bierzemy ostatni próg, którego dolna granica
    (od_arkuszy) nie przekracza liczby arkuszy w zleceniu.
    """
    stawka = progi[0][kolor]
    for prog in progi:
        if arkusze >= prog["od_arkuszy"]:
            stawka = prog[kolor]
    return stawka


def sprawdz_zlecenie(zlecenie: Zlecenie, cennik: dict) -> None:
    """Sprawdza poprawność zlecenia. Przy błędzie zgłasza ValueError z opisem po polsku."""
    if zlecenie.naklad < 1:
        raise ValueError("Nakład musi wynosić co najmniej 1 egzemplarz.")
    if zlecenie.liczba_stron < 1:
        raise ValueError("Liczba stron musi wynosić co najmniej 1.")

    # Każda wybrana opcja musi istnieć w cenniku.
    # Kolory sprawdzamy w pierwszym progu cennika druku, bo każdy próg ma te same kolory.
    opcje = [
        (zlecenie.format, cennik["uzytki_na_arkuszu"], "format"),
        (zlecenie.papier, cennik["papiery"], "papier"),
        (zlecenie.kolor, cennik["druk_za_arkusz"][0], "kolor"),
        (zlecenie.oprawa, cennik["oprawy_za_egzemplarz"], "oprawa"),
        (zlecenie.uszlachetnienie, cennik["uszlachetnienia"], "uszlachetnienie"),
    ]
    for wartosc, dostepne, nazwa in opcje:
        if wartosc not in dostepne:
            raise ValueError(f"Nieznana opcja ({nazwa}): {wartosc}")

    if not czy_dwustronny(zlecenie.kolor) and zlecenie.liczba_stron > 1:
        raise ValueError("Druk jednostronny (np. 4+0) jest możliwy tylko dla 1 strony.")

    # Publikacja oprawiona składa się z arkuszy złożonych na pół, czyli po 4 strony.
    if zlecenie.oprawa != "brak" and zlecenie.liczba_stron % 4 != 0:
        raise ValueError("Przy oprawie liczba stron musi być wielokrotnością 4.")

    # Każda oprawa ma techniczny zakres stron, np. zszywka nie połączy 300 stron.
    limity = cennik["limity_stron_oprawy"].get(zlecenie.oprawa)
    if limity and not limity["min"] <= zlecenie.liczba_stron <= limity["max"]:
        raise ValueError(
            f"Oprawa „{zlecenie.oprawa}” obsługuje od {limity['min']} do {limity['max']} stron."
        )


def wycen(zlecenie: Zlecenie, cennik: dict, kurs_eur: float | None = None) -> Wycena:
    """Liczy pełną wycenę zlecenia według cennika.

    kurs_eur: aktualny kurs z NBP. Gdy go brak, używamy kursu awaryjnego z cennika.
    """
    sprawdz_zlecenie(zlecenie, cennik)

    if kurs_eur is None:
        kurs_eur = cennik["kurs_eur_awaryjny"]
    naddatek = cennik["naddatek_procent"]
    uzytki = cennik["uzytki_na_arkuszu"][zlecenie.format]

    # 1. Ile arkuszy trzeba wydrukować (z zapasem).
    arkusze_netto = liczba_arkuszy(
        zlecenie.naklad, zlecenie.liczba_stron, uzytki, czy_dwustronny(zlecenie.kolor)
    )
    arkusze = z_naddatkiem(arkusze_netto, naddatek)

    # 2. Papier: liczba arkuszy razy cena arkusza.
    cena_papieru = cena_arkusza_papieru(cennik["papiery"][zlecenie.papier], kurs_eur)
    koszt_papieru = arkusze * cena_papieru

    # 3. Druk: liczba arkuszy razy stawka z progu ilościowego,
    # plus stała opłata za przygotowanie zlecenia.
    stawka = stawka_druku(arkusze, zlecenie.kolor, cennik["druk_za_arkusz"])
    koszt_druku = arkusze * stawka + cennik["przygotowanie_zlecenia"]

    # 4. Oprawa: stawka za każdy egzemplarz.
    koszt_oprawy = zlecenie.naklad * cennik["oprawy_za_egzemplarz"][zlecenie.oprawa]

    # 5. Uszlachetnienie. Bez oprawy obejmuje wszystkie arkusze.
    # W publikacji oprawionej uszlachetniamy tylko okładkę, czyli 4 strony egzemplarza.
    uszlachetnienie = cennik["uszlachetnienia"][zlecenie.uszlachetnienie]
    if zlecenie.uszlachetnienie == "brak":
        koszt_uszlachetnien = 0.0
    else:
        if zlecenie.oprawa == "brak":
            arkusze_uszlachetniane = arkusze
        else:
            arkusze_okladki = liczba_arkuszy(zlecenie.naklad, 4, uzytki, True)
            arkusze_uszlachetniane = z_naddatkiem(arkusze_okladki, naddatek)
        za_arkusze = arkusze_uszlachetniane * uszlachetnienie["za_arkusz"]
        koszt_uszlachetnien = za_arkusze + uszlachetnienie["przygotowanie"]

    # 6. Skład: płatny raz za każdą stronę, niezależnie od nakładu.
    koszt_skladu = zlecenie.liczba_stron * cennik["sklad_za_strone"] if zlecenie.sklad else 0.0

    koszty = {
        "papier": round(koszt_papieru, 2),
        "druk": round(koszt_druku, 2),
        "oprawa": round(koszt_oprawy, 2),
        "uszlachetnienia": round(koszt_uszlachetnien, 2),
        "skład": round(koszt_skladu, 2),
    }

    # 7. Ceny końcowe: koszt własny, marża, VAT.
    koszt_wlasny = sum(koszty.values())
    marza = koszt_wlasny * cennik["marza_procent"] / 100
    cena_netto = koszt_wlasny + marza
    vat = cena_netto * cennik["vat_procent"] / 100
    cena_brutto = cena_netto + vat

    return Wycena(
        arkusze=arkusze,
        koszty=koszty,
        koszt_wlasny=round(koszt_wlasny, 2),
        marza=round(marza, 2),
        cena_netto=round(cena_netto, 2),
        vat=round(vat, 2),
        cena_brutto=round(cena_brutto, 2),
        cena_netto_za_sztuke=round(cena_netto / zlecenie.naklad, 2),
        cena_brutto_za_sztuke=round(cena_brutto / zlecenie.naklad, 2),
    )
