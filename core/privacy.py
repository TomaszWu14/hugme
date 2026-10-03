"""Maskowanie danych osobowych ZANIM tekst trafi do bazy albo do AI.

Maskujemy: PESEL, telefon, e-mail, adres i kod pocztowy, imię po słowach typu „syn/córka”,
nazwisko po „dr”. Oryginał nigdzie nie jest zapisywany."""
import re

_UP = "A-ZĄĆĘŁŃÓŚŹŻ"
_LO = "a-ząćęłńóśźż"
_NAME = rf"[{_UP}][{_LO}]{{1,20}}"

KIN = (
    r"syn|syna|synowi|synem|synek|synka|córka|córki|córce|córkę|córką|córeczka|córeczki|"
    r"dziecko|dziecka|wnuk|wnuka|wnuczka|wnuczki|mąż|męża|mężem|żona|żony|żoną|"
    r"brat|brata|siostra|siostry|mama|mamy|tata|taty|ojciec|ojca|matka|matki|"
    r"mam na imię|nazywam się|ma na imię|o imieniu|imieniem"
)

RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RE_ELEVEN = re.compile(r"(?<!\d)\d{11}(?!\d)")
RE_PHONE = re.compile(r"(?<![\d\w])(?:\+?48[\s-]?)?\(?\d{2,3}\)?(?:[\s-]?\d){6,7}(?![\d])")
RE_POSTAL = re.compile(r"(?<!\d)\d{2}-\d{3}(?!\d)")
RE_ADDRESS = re.compile(
    rf"\b(?:ul\.|ulica|ulicy|al\.|aleja|alei|os\.|osiedle|osiedlu|pl\.|plac|placu)\s*"
    rf"[{_UP}0-9][\w{_LO}{_UP}.-]*(?:\s+[{_UP}][\w{_LO}.-]*){{0,3}}(?:\s+\d+[a-zA-Z]?(?:\s*/\s*\d+)?)?"
)
RE_KIN_NAME = re.compile(rf"(?i:\b({KIN}))(\s*[:,-]?\s*)({_NAME}(?:\s+{_NAME})?)")
RE_DOCTOR = re.compile(rf"\b(dr|doktor|doktora|doktorem|lek\.|prof\.)(\s+(?:n\.\s*med\.\s+|hab\.\s+)?)({_NAME}(?:-{_NAME})?)")

# Słowa pisane wielką literą po „syn/córka”, które nie są imionami (np. „córka Downa” – raczej nie, ale „syn Kowalskich”).
_NOT_NAMES = {"Downa", "Down", "Jest", "Ma", "Ale", "Bo", "I", "W", "Na", "Z", "Od", "Do", "Po", "To"}

LABELS = {
    "PESEL": "numer PESEL", "NUMER": "długi numer", "TELEFON": "numer telefonu", "E-MAIL": "adres e-mail",
    "ADRES": "adres", "KOD": "kod pocztowy", "IMIĘ": "imię", "NAZWISKO": "nazwisko",
}


def pesel_valid(digits):
    weights = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
    check = (10 - sum(int(d) * w for d, w in zip(digits, weights)) % 10) % 10
    return check == int(digits[10])


def mask(text):
    """Zwraca (tekst_zamaskowany, lista_wykrytych_rodzajów)."""
    found = []

    def sub(regex, repl_fn, s):
        return regex.sub(repl_fn, s)

    def tag(kind):
        found.append(kind)
        return f"[{kind}]"

    text = sub(RE_EMAIL, lambda m: tag("E-MAIL"), text)
    text = sub(RE_ELEVEN, lambda m: tag("PESEL" if pesel_valid(m.group()) else "NUMER"), text)
    text = sub(RE_POSTAL, lambda m: tag("KOD"), text)
    text = sub(RE_PHONE, lambda m: tag("TELEFON") if len(re.sub(r"\D", "", m.group())) >= 9 else m.group(), text)
    text = sub(RE_ADDRESS, lambda m: tag("ADRES"), text)

    def kin(m):
        if m.group(3).split()[0] in _NOT_NAMES:
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}{tag('IMIĘ')}"
    text = sub(RE_KIN_NAME, kin, text)
    text = sub(RE_DOCTOR, lambda m: f"{m.group(1)}{m.group(2)}{tag('NAZWISKO')}", text)
    return text, found


def describe(found):
    """Krótki, łagodny opis tego, co ukryliśmy (dla komunikatu w UI)."""
    kinds = []
    for k in found:
        label = LABELS.get(k, k)
        if label not in kinds:
            kinds.append(label)
    return ", ".join(kinds)


if __name__ == "__main__":
    t, f = mask("Mój syn Jaś ma 8 lat, PESEL 44051401359, tel. 600 123 456, jan@x.pl, ul. Długa 5/3, 30-001 Kraków, dr Nowak")
    assert "Jaś" not in t and "44051401359" not in t and "600 123 456" not in t and "Długa" not in t and "Nowak" not in t, t
    print(t, f)
