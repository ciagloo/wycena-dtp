"""Interfejs użytkownika aplikacji Wycena DTP (Streamlit).

Streamlit uruchamia ten plik od góry do dołu przy każdej zmianie w formularzu,
dlatego wycena odświeża się od razu po zmianie dowolnego pola.
Uruchomienie: streamlit run app.py
"""

import pandas as pd
import streamlit as st

from wycena.charts import wykres_kosztow, wykres_produktow
from wycena.history import statystyki, wczytaj_historie, zapisz_wycene
from wycena.money import format_zl
from wycena.offer_pdf import generuj_oferte
from wycena.price_list import wczytaj_cennik
from wycena.pricing import Zlecenie, wycen

st.set_page_config(page_title="Wycena DTP", layout="wide")
st.title("Wycena DTP")
st.caption("Wycena zleceń poligraficznych według cennika studia. Druk cyfrowy, arkusz SRA3.")

cennik = wczytaj_cennik()

# Listy opcji bierzemy z cennika, więc nowa pozycja w cenniku od razu pojawi się w formularzu.
# W progach druku pomijamy klucz "od_arkuszy", bo to granica progu, a nie kolor.
kolory = [klucz for klucz in cennik["druk_za_arkusz"][0] if klucz != "od_arkuszy"]

zakladka_wycena, zakladka_historia = st.tabs(["Wycena", "Historia i statystyki"])
kolumna_formularz, kolumna_wynik = zakladka_wycena.columns([1, 1.6], gap="large")


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
        wynik = None

    if wynik is not None:
        st.subheader("Wycena")
        cena_1, cena_2, cena_3 = st.columns(3)
        cena_1.metric("Cena netto", format_zl(wynik.cena_netto))
        cena_2.metric("Cena brutto", format_zl(wynik.cena_brutto))
        cena_3.metric("Za sztukę netto", format_zl(wynik.cena_netto_za_sztuke))
        st.caption(
            f"Arkusze SRA3 do druku: {wynik.arkusze} (z naddatkiem). "
            f"Kurs EUR: {format_zl(cennik['kurs_eur_awaryjny'])} (kurs z cennika)."
        )

        st.plotly_chart(wykres_kosztow(wynik.koszty, wynik.koszt_wlasny), width="stretch")

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
        przycisk_pdf, przycisk_zapis = st.columns(2)
        przycisk_pdf.download_button(
            "Pobierz ofertę PDF",
            data=oferta,
            file_name=f"oferta_{zlecenie.produkt}_{zlecenie.naklad}szt.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
        )
        # st.button zwraca True tylko w tym przebiegu skryptu, w którym go kliknięto.
        if przycisk_zapis.button("Zapisz w historii", width="stretch"):
            zapisz_wycene(zlecenie, wynik, klient)
            st.toast("Wycena zapisana w historii.")

# Druga zakładka: historia wycen i statystyki
with zakladka_historia:
    historia = wczytaj_historie()
    dane = statystyki(historia)

    if dane["liczba_wycen"] == 0:
        st.info("Historia jest pusta. Zapisz pierwszą wycenę przyciskiem „Zapisz w historii”.")
    else:
        stat_1, stat_2, stat_3 = st.columns(3)
        stat_1.metric("Liczba wycen", dane["liczba_wycen"])
        stat_2.metric("Średnia wartość netto", format_zl(dane["srednia_netto"]))
        stat_3.metric("Łączna wartość netto", format_zl(dane["suma_netto"]))

        st.plotly_chart(wykres_produktow(dane["produkty"]), width="stretch")

        st.subheader("Zapisane wyceny")
        widok = historia.drop(columns=["id"]).rename(
            columns={
                "data": "Data",
                "klient": "Klient",
                "produkt": "Produkt",
                "format": "Format",
                "liczba_stron": "Strony",
                "naklad": "Nakład",
                "papier": "Papier",
                "kolor": "Kolor",
                "oprawa": "Oprawa",
                "uszlachetnienie": "Uszlachetnienie",
                "cena_netto": "Netto",
                "cena_brutto": "Brutto",
            }
        )
        widok["Netto"] = widok["Netto"].apply(format_zl)
        widok["Brutto"] = widok["Brutto"].apply(format_zl)
        st.dataframe(widok, hide_index=True, width="stretch")
