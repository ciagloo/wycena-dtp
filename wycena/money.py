"""Formatowanie kwot w polskim zapisie, np. 1 234,50 zł."""


def format_zl(kwota: float) -> str:
    """Zamienia liczbę na tekst z dwoma miejscami po przecinku i spacją co trzy cyfry."""
    # Najpierw zapis angielski: 1,234.50
    tekst = f"{kwota:,.2f}"
    # Potem zamiana separatorów na polskie: przecinek tysięcy na spację, kropka na przecinek
    tekst = tekst.replace(",", " ").replace(".", ",")
    return f"{tekst} zł"
