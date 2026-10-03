"""Dane przykładowe. Wszystko jest FIKCYJNE i oznaczone w interfejsie jako „PRZYKŁAD”.
Zgłoszenia opisują sytuacje grup, nie konkretnych osób."""
from core.db import now

USERS = [
    # (name, role, org, areas, email)
    ("Anna – mama, powiat wadowicki", "mieszkaniec", None, "rodziny-zd", "anna@przyklad.invalid"),
    ("Marta – Fundacja Razem Bliżej", "ngo", "Fundacja Razem Bliżej (PRZYKŁAD)", "rodziny-zd,samotnosc",
     "marta@przyklad.invalid"),
    ("Piotr – Urząd Gminy Przykładowo", "gmina", "Gmina Przykładowo (PRZYKŁAD)", "seniorzy,wies",
     "piotr@przyklad.invalid"),
    ("Ewa – ekspertka ds. integracji", "ekspert", "Niezależna ekspertka (PRZYKŁAD)", "rodziny-zd,psychiczne",
     "ewa@przyklad.invalid"),
    ("Joanna – koordynatorka Hubu ROPS", "admin", "ROPS Kraków – Hub Innowacji Społecznych", "",
     "joanna@przyklad.invalid"),
]


def run(con):
    con.executemany(
        "INSERT INTO users (name, role, org, areas, email) VALUES (?, ?, ?, ?, ?)", USERS
    )
    con.commit()
    _ = now  # dalsze dane przykładowe dochodzą w kolejnych etapach
