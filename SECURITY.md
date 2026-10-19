# Bezpieczeństwo

## Zgłaszanie podatności

Podatności zgłaszaj **prywatnie**, nie przez publiczne issue ani PR:
GitHub → zakładka *Security* → **Report a vulnerability**
(<https://github.com/TomaszWu14/hugme/security/advisories/new>).

Opisz: adres strony lub plik, kroki odtworzenia, skutek i wersję (SHA commita). Nie dołączaj prawdziwych
danych osobowych — aplikacja dotyczy spraw wrażliwych. Odpowiedź dostaniesz najczęściej do 7 dni.

## Zakres

Wspierana jest gałąź domyślna `main` i wdrożenie z niej zbudowane; poprawki nie trafiają do starszych commitów.
Testy w dobrej wierze tylko na publicznym demo (dane fikcyjne), bez ataków odmowy usługi.

## Automatyczne kontrole

Opis skanów w CI i wbudowanych zabezpieczeń: sekcja [Bezpieczeństwo](README.md#bezpieczeństwo) w `README.md`.
