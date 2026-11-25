# Wycena DTP

Aplikacja do wyceny zleceń poligraficznych i generowania ofert dla małego studia DTP.

Projekt zaliczeniowy z przedmiotu **Advanced Python for Business** (prowadzący: mgr Piotr Żmijewski),
Uczelnia Łazarskiego, Zarządzanie, specjalność AI w biznesie.
Autor: Jakub Ciągło.

## Problem

W małym studiu DTP wyceny zleceń (papier, druk, oprawa, uszlachetnienia, skład) przygotowuje się ręcznie.
Zajmuje to czas, a ceny tego samego zlecenia bywają różne w zależności od osoby i dnia.
Aplikacja liczy cenę według jednego cennika, pokazuje strukturę kosztów i generuje ofertę PDF dla klienta.

## Funkcje

- formularz zlecenia: rodzaj publikacji (z typowymi parametrami), format, liczba stron, nakład, papier, kolor, oprawa, uszlachetnienia
- kontrola wykonalności, np. zakres stron dla danej oprawy
- silnik wyceny: koszt papieru, druku, oprawy, uszlachetnień i składu, marża, cena netto, brutto i za sztukę
- cennik w pliku `dane/cennik.json`, edytowalny bez zmiany kodu
- wykres struktury kosztów
- oferta PDF dla klienta
- historia wycen w SQLite i proste statystyki
- kurs EUR z API NBP (część papierów wyceniana w euro)

## Jak liczona jest wycena

Model zakłada druk cyfrowy na arkuszach SRA3 (320 x 450 mm).

1. **Arkusze**: nakład x liczba stron / (użytki na arkuszu x liczba zadrukowanych stron arkusza),
   w górę do pełnego arkusza, plus naddatek 5% na odpady.
2. **Papier**: arkusze x cena arkusza (papiery w EUR przeliczane po kursie NBP).
3. **Druk**: arkusze x stawka za kolor z progu ilościowego + opłata za przygotowanie zlecenia.
4. **Oprawa**: nakład x stawka za egzemplarz.
5. **Uszlachetnienia**: arkusze x stawka (w publikacji oprawionej tylko okładka) + przygotowanie.
6. **Skład**: liczba stron x stawka za stronę.
7. **Cena**: koszt własny + marża = netto; netto + VAT = brutto; cena za sztukę = cena / nakład.

Stawki pochodzą z pliku `dane/cennik.json`. Źródła i sposób uśrednienia opisuje `dane/ZRODLA_CEN.md`.

## Struktura projektu

```
wycena-dtp/
    app.py              interfejs użytkownika (Streamlit)
    requirements.txt    lista bibliotek
    pyproject.toml      ustawienia lintera ruff i pytest
    dane/
        cennik.json                 stawki (edytowalne bez zmiany kodu)
        przykladowe_zlecenia.json   zlecenia do demo i testów
        ZRODLA_CEN.md               źródła stawek
        fonty/                      font Fira Sans (licencja OFL) do oferty PDF
    wycena/             logika aplikacji
        pricing.py      silnik wyceny
        price_list.py   wczytanie cennika
        offer_pdf.py    generowanie oferty PDF
        history.py      historia wycen i statystyki
        nbp.py          kurs EUR z API NBP
        money.py        formatowanie kwot (1 234,50 zł)
    tests/              testy jednostkowe (pytest)
```

## Instalacja (Windows, PowerShell)

Wymagany Python 3.10 lub nowszy.

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uruchomienie

```
streamlit run app.py
```

Aplikacja otworzy się w przeglądarce pod adresem http://localhost:8501.

## Testy i jakość kodu

```
python -m pytest
ruff check .
```

## Status

Projekt w budowie. Gotowe: struktura projektu, cennik, silnik wyceny z testami, interfejs z wykresem kosztów,
oferta PDF.
Kolejne etapy: historia, API NBP, dokumentacja.
