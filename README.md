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

- formularz zlecenia: rodzaj publikacji, format, liczba stron, nakład, papier, kolor, oprawa, uszlachetnienia
- silnik wyceny: koszt papieru, druku, oprawy, uszlachetnień i składu, marża, cena netto, brutto i za sztukę
- cennik w pliku `dane/cennik.json`, edytowalny bez zmiany kodu
- wykres struktury kosztów
- oferta PDF dla klienta
- historia wycen w SQLite i proste statystyki
- kurs EUR z API NBP (część papierów wyceniana w euro)

## Struktura projektu

```
wycena-dtp/
    app.py              interfejs użytkownika (Streamlit)
    requirements.txt    lista bibliotek
    dane/               cennik i dane przykładowe
    wycena/             logika aplikacji
        pricing.py      silnik wyceny
        price_list.py   wczytanie cennika
        offer_pdf.py    generowanie oferty PDF
        history.py      historia wycen i statystyki
        nbp.py          kurs EUR z API NBP
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

## Testy

```
python -m pytest
```

## Status

Projekt w budowie. Kolejne etapy: silnik wyceny z testami, interfejs, oferta PDF, historia, API NBP, dokumentacja.
