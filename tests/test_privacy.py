import pytest

from core.privacy import describe, mask, pesel_valid


@pytest.mark.parametrize("text, secret, kind", [
    ("PESEL dziecka 44051401359", "44051401359", "PESEL"),
    ("dzwońcie 600 123 456", "600 123 456", "TELEFON"),
    ("tel. +48 600-123-456", "600-123-456", "TELEFON"),
    ("pisz na anna.k@example.com", "anna.k@example.com", "E-MAIL"),
    ("mieszkamy przy ul. Długa 5/3", "Długa", "ADRES"),
    ("kod 30-001 Kraków", "30-001", "KOD"),
    ("moja córka Zosia chodzi do szkoły", "Zosia", "IMIĘ"),
    ("synek Kacper ma 6 lat", "Kacper", "IMIĘ"),
    ("byliśmy u dr Kowalskiej", "Kowalskiej", "NAZWISKO"),
])
def test_masks_personal_data(text, secret, kind):
    masked, found = mask(text)
    assert secret not in masked
    assert kind in found


def test_keeps_group_description_untouched():
    text = "Rodzice dzieci z zespołem Downa w naszej gminie jeżdżą do wielu lekarzy."
    assert mask(text) == (text, [])


def test_syndrome_name_is_not_treated_as_child_name():
    masked, _ = mask("córka Downa nie dotyczy – mamy dziecko z zespołem Downa")
    assert "zespołem Downa" in masked


def test_pesel_checksum():
    assert pesel_valid("44051401359")
    assert not pesel_valid("44051401358")


def test_describe_is_human_readable():
    assert describe(["PESEL", "IMIĘ", "IMIĘ"]) == "numer PESEL, imię"
