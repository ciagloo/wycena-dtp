"""Interfejs użytkownika aplikacji Wycena DTP (Streamlit).

Streamlit uruchamia ten plik od góry do dołu przy każdej zmianie w formularzu,
dlatego wycena odświeża się od razu po zmianie dowolnego pola.
Uruchomienie: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from wycena.money import format_zl
from wycena.offer_pdf import generuj_oferte
from wycena.price_list import wczytaj_cennik
from wycena.pricing import Zlecenie, wycen

KOLOR_SLUPKOW = "#257de0"

st.set_page_config(page_title="Wycena DTP", layout="wide")
st.title("Wycena DTP")
st.caption("Wycena zleceń poligraficznych według cennika studia. Druk cyfrowy, arkusz SRA3.")

cennik = wczytaj_cennik()

# Listy opcji bierzemy z cennika, więc nowa pozycja w cenniku od razu pojawi się w formularzu.
# W progach druku pomijamy klucz "od_arkuszy", bo to granica progu, a nie kolor.
kolory = [klucz for klucz in cennik["druk_za_arkusz"][0] if klucz != "od_arkuszy"]

kolumna_formularz, kolumna_wynik = st.columns([1, 1.6], gap="large")


def lista_wyboru(etykieta: str, opcje: list[str], domyslna: str, produkt: str) -> str:
    """Pole wyboru z wartością domyślną zależną od rodzaju publikacji.

    Streamlit zapamiętuje wartość pola po jego kluczu (key). Klucz zawiera nazwę produktu,
    więc po zmianie produktu pole startuje od nowa z domyślną wartością tego produktu.
    """
    return st.selectbox(etykieta, opcje, index=opcje.index(domyslna), key=f"{etykieta}_{produkt}")


# Lewa kolumna: parametry zlecenia
with kolumna_formularz:
    st.subheader("Parametry zlecenia")
    produkt = st.selectbox("Rodzaj publikacji", list(cennik["produkty"]))
    # Typowe parametry wybranego produktu z cennika, np. książka: A5, 160 stron, klejona.
    domyslne = cennik["produkty"][produkt]

    format_ = lista_wyboru("Format", list(cennik["uzytki_na_arkuszu"]), domyslne["format"], produkt)
    liczba_stron = st.number_input(
        "Liczba stron",
        min_value=1,
        value=domyslne["liczba_stron"],
        step=1,
        key=f"strony_{produkt}",
    )
    naklad = st.number_input(
        "Nakład (egz.)", min_value=1, value=domyslne["naklad"], step=50, key=f"naklad_{produkt}"
    )
    papier = lista_wyboru("Papier", list(cennik["papiery"]), domyslne["papier"], produkt)
    kolor = lista_wyboru("Kolor druku", kolory, domyslne["kolor"], produkt)
    oprawa = lista_wyboru(
        "Oprawa", list(cennik["oprawy_za_egzemplarz"]), domyslne["oprawa"], produkt
    )
    uszlachetnienie = lista_wyboru(
        "Uszlachetnienie", list(cennik["uszlachetnienia"]), domyslne["uszlachetnienie"], produkt
    )
    sklad = st.checkbox("Skład wykonuje studio", value=True)
    klient = st.text_input("Klient (do oferty, opcjonalnie)")

zlecenie = Zlecenie(
    produkt=produkt,
    format=format_,
    liczba_stron=int(liczba_stron),
    naklad=int(naklad),
    papier=papier,
    kolor=kolor,
    oprawa=oprawa,
    uszlachetnienie=uszlachetnienie,
    sklad=sklad,
)

# Prawa kolumna: wynik wyceny
with kolumna_wynik:
    try:
        wynik = wycen(zlecenie, cennik)
    except ValueError as blad:
        # Błędne dane (np. oprawa przy 6 stronach) pokazujemy jako komunikat zamiast awarii.
        st.error(str(blad))
        st.stop()

    st.subheader("Wycena")
    cena_1, cena_2, cena_3 = st.columns(3)
    cena_1.metric("Cena netto", format_zl(wynik.cena_netto))
    cena_2.metric("Cena brutto", format_zl(wynik.cena_brutto))
    cena_3.metric("Za sztukę netto", format_zl(wynik.cena_netto_za_sztuke))
    st.caption(
        f"Arkusze SRA3 do druku: {wynik.arkusze} (z naddatkiem). "
        f"Kurs EUR: {format_zl(cennik['kurs_eur_awaryjny'])} (kurs z cennika)."
    )

    # Tabela kosztów: składowe, marża i VAT.
    wiersze = [
        {"Pozycja": nazwa.capitalize(), "Kwota": kwota} for nazwa, kwota in wynik.koszty.items()
    ]
    wiersze += [
        {"Pozycja": "Koszt własny razem", "Kwota": wynik.koszt_wlasny},
        {"Pozycja": f"Marża ({cennik['marza_procent']}%)", "Kwota": wynik.marza},
        {"Pozycja": "Cena netto", "Kwota": wynik.cena_netto},
        {"Pozycja": f"VAT ({cennik['vat_procent']}%)", "Kwota": wynik.vat},
        {"Pozycja": "Cena brutto", "Kwota": wynik.cena_brutto},
    ]
    tabela = pd.DataFrame(wiersze)
    tabela["Kwota"] = tabela["Kwota"].apply(format_zl)

    # Wykres: tylko składowe większe od zera, posortowane od największej.
    koszty = pd.DataFrame(
        {
            "Składnik": [nazwa.capitalize() for nazwa in wynik.koszty],
            "Kwota": list(wynik.koszty.values()),
        }
    )
    koszty = koszty[koszty["Kwota"] > 0].sort_values("Kwota")
    koszty["Udział"] = koszty["Kwota"] / wynik.koszt_wlasny * 100
    koszty["Opis"] = [
        f"{format_zl(k)} ({u:.0f}%)" for k, u in zip(koszty["Kwota"], koszty["Udział"], strict=True)
    ]

    wykres = px.bar(
        koszty,
        x="Kwota",
        y="Składnik",
        orientation="h",
        text="Opis",
        title="Struktura kosztu własnego",
        custom_data=["Opis"],
    )
    wykres.update_traces(
        marker_color=KOLOR_SLUPKOW,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{customdata[0]}<extra></extra>",
    )
    wykres.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis={"showticklabels": False, "showgrid": False},
        margin={"l": 0, "r": 110, "t": 50, "b": 0},
        height=80 + 50 * len(koszty),
        bargap=0.35,
    )
    st.plotly_chart(wykres, width="stretch")

    st.dataframe(tabela, hide_index=True, width="stretch")

    # Oferta PDF dla klienta: tylko parametry i cena, bez kosztów wewnętrznych i marży.
    oferta = generuj_oferte(
        zlecenie,
        wynik,
        studio=cennik["studio"],
        vat_procent=cennik["vat_procent"],
        dni_waznosci=cennik["waznosc_oferty_dni"],
        klient=klient,
    )
    st.download_button(
        "Pobierz ofertę PDF",
        data=oferta,
        file_name=f"oferta_{zlecenie.produkt}_{zlecenie.naklad}szt.pdf",
        mime="application/pdf",
        type="primary",
    )
