"""Testy formatowania kwot."""

from wycena.money import format_zl


def test_format_zl():
    assert format_zl(0) == "0,00 zł"
    assert format_zl(12.5) == "12,50 zł"
    assert format_zl(1234.567) == "1 234,57 zł"
    assert format_zl(1250000) == "1 250 000,00 zł"
