# HugMe — burza mózgów (100 pytań)

Jak odpowiadać: wpisz po `ODP:`.
- Puste `ODP:` = akceptuję propozycję.
- `ok` = akceptuję propozycję.
- Własny tekst = nadpisuje propozycję.
⚡ = rozstrzygnąć najpierw (termin: 4.10.2026, 11:00).

---

## A. Czas, zespół, zakres ⚡

1. ⚡ Ile osób w zespole i kto co robi (kod, UX, slajdy, film)?
   Propozycja: ja kod; Ty decyzje + demo + film
   ODP:wszystko jedna osoba

2. ⚡ Ile godzin realnie masz do 11:00 (ze snem)?
   Propozycja: ~16 h
   ODP: 16

3. ⚡ Wszystkie 7 modułów to wymóg, czy mogą być płytsze?
   Propozycja: wszystkie 7, moduły 4–7 „cienkie, ale działające”
   ODP: wydaje mi sie że tak

4. ⚡ Co ważniejsze: liczba modułów (40%) czy jakość matchmakingu?
   Propozycja: matchmaking dopracowany, reszta cienka
   ODP:nie wiem ,tak aby zwiekszyc punktacje

5. ⚡ Coś w repo do zachowania (main.py, .idea)?
   Propozycja: nie — main.py to szablon PyCharm, do usunięcia
   ODP:tak

6. ⚡ O której zamrażamy kod, żeby zdążyć z filmem i slajdami?
   Propozycja: 4.10, 07:00
   ODP:na bieżąco ustalimy bo moz emy skonczyc wcześniej

7. Branch + PR-y czy hackathonowo na main?
   Propozycja: main, commit po każdym module
   ODP:nie,mamy limi 10-15 commitów,zawsze pytaj przed pushem

8. Repo publiczne na GitHubie od razu?
   Propozycja: prywatne do oddania, potem wg odpowiedzi o licencji
   ODP:tak, ma być publiczne

9. Jest checkpoint z mentorami w trakcie (godzina)?
   Propozycja: ?
   ODP: nie wiem,obojętne

10. Co tniemy najpierw, gdy zabraknie czasu?
    Propozycja: kolejka e-mail, import CSV, mapa powiat×obszar
    ODP:nic,zdązymy

## B. Ocena i jury

11. Masz pełny regulamin i rozpisane kryteria 40/20/20/10/10 (co to ostatnie 10+10)?
    Propozycja: podeślij — wpiszę do KRYTERIA.md
    ODP:• Stopień spełnienia wyzwania - 40%. Brana jest pod uwagę jakość działania kluczowych elementów oraz liczba dostarczonych dodatkowych funkcjonalności • Potencjał wdrożeniowy - 20%. Ocena stopnia gotowości rozwiązania do wdrożenia. Wyżej punktowane będą produkty nadające się do praktycznego użytku, które charakteryzują się skalowalnością, elastycznością, optymalizacją oraz wysoką efektywnością kosztową i prostotą utrzymania. • Dostępność i intuicyjność prototypu – 20%. Weryfikowane jest, czy interfejs narzędzia jest przejrzysty i łatwy w obsłudze dla wszystkich docelowych grup odbiorców, niezależnie od ich wieku i poziomu umiejętności cyfrowych. Szczególna uwaga zwracana jest na zaprojektowanie narzędzia z myślą o docelowych standardach dostępności cyfrowej WCAG 2.1 na poziomie AA, aby nie stwarzało ono barier użytkowych.  • Kryteria premiujące - 20%, w tym: - Atrakcyjność, pomysłowość i jakość interfejsu - 10% . Kryterium to promuje nowatorskie, nieszablonowe podejście do przedstawionego wyzwania oraz wizualną atrakcyjność dostarczonych makiet UX/UI , - Jakość dostarczonych materiałów oraz MVP - 10%. Ocenie podlega sposób komunikacji koncepcji oraz jakość materiałów przesłanych do oceny. 

12. Jury ogląda działającą aplikację pod URL czy tylko film + PDF?
    Propozycja: jedno i drugie, URL na Coolify
    ODP:tak

13. „Moduł” liczony po nazwie z briefu — wystarczy mapowanie w README?
    Propozycja: tak, tabela 1:1
    ODP:ok

14. Kto z ROPS w jury i czego mogą szukać (np. zgodności z Mapą Wyzwań)?
    Propozycja: ?
    ODP:nie wiem

15. Oceniana innowacyjność AI czy działanie bez AI?
    Propozycja: pokazujemy oba tryby
    ODP:tak

16. Trzeba pokazać skalowalność na całe województwo?
    Propozycja: tak — w docs i w danych z różnych powiatów
    ODP:ok

## C. Użytkownicy i role

17. Przełącznik ról zawsze widoczny (pasek „Tryb demo”)?
    Propozycja: tak, górny pasek
    ODP:

18. Ekspert ma własny widok „pytania czekające na mnie”?
    Propozycja: tak, prosta lista wątków
    ODP:ok

19. Czym różnią się widoki NGO i Gminy?
    Propozycja: Gmina → Pośrednik + nabory; NGO → Kreator + Tester
    ODP:ok

20. Mieszkaniec może szukać/czytać bez logowania?
    Propozycja: tak, logowanie dopiero do zapisu
    ODP:ok

21. Rodzic może być anonimowy w wątku z Hubem?
    Propozycja: tak, pseudonim
    ODP:ok

22. Koordynatorka ROPS widzi wszystko czy tylko swój obszar?
    Propozycja: wszystko, jeden admin
    ODP:ok

23. Osobna rola „moderator”?
    Propozycja: nie, tylko wzmianka w KOSZTY
    ODP:ok

24. Jedna osoba może mieć kilka ról?
    Propozycja: nie w prototypie
    ODP:ok

## D. Matchmaking (obowiązkowy)

25. Ile wyników pokazujemy?
    Propozycja: top 5 innowacji; po 3 zgłoszenia / materiały / ekspertów
    ODP:ok

26. Forma trafności: procent, gwiazdki, słowa?
    Propozycja: słowa („bardzo pasuje”) + pasek z tekstem, nie sam kolor
    ODP:ok

27. Próg „luki” (zgłoszenie bez dobrego dopasowania)?
    Propozycja: najlepszy wynik < 0,35 lub same oceny „niepomocne”
    ODP:ok

28. Polski stemming: własny prosty czy biblioteka (pystempel)?
    Propozycja: prosty regułowy + słownik pojęć, bez zależności
    ODP:ok

29. Kto pisze słownik pojęć i jak duży?
    Propozycja: ja, ~15 tematów × ~10 słów
    ODP:ok

30. Powiat i obszar: wybór w formularzu czy wykrywanie z tekstu?
    Propozycja: powiat z listy (opcjonalny), obszar wykrywany + do poprawienia
    ODP:

31. „Pomocne/niepomocne” zmienia ranking (uczenie)?
    Propozycja: nie — tylko pomiar i metryka w panelu
    ODP:ok

32. Wyniki na żywo przy pisaniu czy po kliknięciu „Szukaj”?
    Propozycja: po kliknięciu, bez JS jako wymogu
    ODP:ok

33. Ile przypadków w teście trafności i jaki próg top 3?
    Propozycja: 10 opisów, cel ≥ 80%
    ODP:ok

34. Podobne zgłoszenia pokazują treść innych osób?
    Propozycja: tak (fikcyjne); w realu tylko zatwierdzone
    ODP:

35. Zgłoszenie publiczne od razu czy po moderacji?
    Propozycja: po zatwierdzeniu przez admina
    ODP:ok

36. Co przy zbyt krótkim opisie (np. „lekarz”)?
    Propozycja: łagodna podpowiedź + przykład
    ODP:ok

## E. Zasobnik wiedzy

37. Ile kart wyzwań Małopolski?
    Propozycja: 7 obszarów z briefu
    ODP:ok

38. Filmy: osadzony YouTube (CSP) czy linki?
    Propozycja: youtube-nocookie iframe (frame-src w CSP) + tekstowy opis
    ODP:ok

39. Filtry Biblioteki?
    Propozycja: obszar, powiat, etap, grupa odbiorców
    ODP:ok

40. Ścieżka rodziny: statyczny tekst czy oś z linkami?
    Propozycja: oś 4 kroków z linkami do innowacji i materiałów
    ODP:oś

41. Kto pisze treść ścieżki (treść medyczna — ostrożnie)?
    Propozycja: ja, ogólnikowo, z dopiskiem „PRZYKŁAD — skonsultuj z lekarzem”
    ODP:ok

42. Materiały edukacyjne jako PDF czy HTML?
    Propozycja: HTML (dostępniejszy)
    ODP:ok

43. Trendy w Zasobniku czy w Panelu?
    Propozycja: w panelu admina (zgodnie z briefem)
    ODP:ok

## F. Kreator pomysłów

44. Fiszka i Kanwa: jeden formularz krokowy czy dwa osobne?
    Propozycja: kroki: fiszka → kanwa (opcjonalna)
    ODP:ok

45. Które pola Kanwy Innowacji Społecznych?
    Propozycja: standardowe 9–11 pól; podeślij wersję ROPS, jeśli masz
    ODP:ok

46. Pomysł publiczny po zapisie?
    Propozycja: prywatny + widoczny dla Hubu; publiczny po zgodzie
    ODP:tyko publiczny

47. Regułowy zamiennik asystenta AI bez klucza?
    Propozycja: szablony pytań wg etapu i pustych pól
    ODP:ok

48. Jakie pola ma wzorcowy nabór (generator wniosków)?
    Propozycja: tytuł, problem, grupa, działania, rezultaty, budżet opisowy, partnerzy
    ODP:ok

49. „Złożenie wniosku” = zmiana statusu + powiadomienie?
    Propozycja: tak
    ODP:ok

50. Wydruk: CSS print czy generowany PDF?
    Propozycja: print CSS
    ODP:ok

51. Wartości etapu pomysłu?
    Propozycja: pomysł / prototyp / test / wdrożenie
    ODP:ok

## G. Tester innowacji

52. Kto może testować?
    Propozycja: każdy zalogowany
    ODP:ok

53. Ocena 1–5 publiczna (średnia przy innowacji)?
    Propozycja: tak, średnia + liczba ocen
    ODP:ok

54. Zgłoszenie do testu ma terminy/zapisy na pilotaż?
    Propozycja: nie — formularz + status
    ODP:ok

## H. Komunikacja

55. Wątki płaskie czy zagnieżdżone?
    Propozycja: płaskie
    ODP:ok

56. Powiadomienia w aplikacji: przy odświeżeniu czy polling JS?
    Propozycja: licznik przy odświeżeniu, bez JS
    ODP:ok

57. Kolejka e-mail: tabela w DB + podgląd w panelu, bez prawdziwego SMTP?
    Propozycja: tak, SMTP opisany w docs
    ODP:ok

58. Gdzie przycisk „obserwuj obszar”?
    Propozycja: na karcie obszaru + w profilu
    ODP:ok

59. Ustawienia powiadomień (wyłącz e-mail)?
    Propozycja: nie w prototypie
    ODP:ok

60. Ekspert dostaje powiadomienie o pytaniu w swoim obszarze?
    Propozycja: tak, eksperci mają przypisane obszary
    ODP:ok

## I. Panel administratora

61. Skrzynka: jedna lista z typami czy zakładki?
    Propozycja: jedna lista + filtr typu
    ODP:ok

62. Statusy zgłoszenia?
    Propozycja: nowe / w analizie / połączone z rozwiązaniem / luka / zamknięte
    ODP:ok

63. Szybka edycja Biblioteki: inline czy formularz?
    Propozycja: formularz na osobnej stronie
    ODP:ok

64. Mapa powiat × obszar: tabela-heatmapa czy SVG mapy Małopolski?
    Propozycja: tabela z liczbami (dostępna); SVG jeśli zostanie czas
    ODP:ok

65. Eksport CSV — czego?
    Propozycja: zgłoszenia, luki, oceny dopasowań
    ODP:nic na razie

66. Import Biblioteki ROPS — format na start?
    Propozycja: CSV z mapowaniem kolumn; JSON drugi
    ODP:ok

67. Panel pokazuje metrykę trafności (% „pomocne”)?
    Propozycja: tak — mocny argument dla jury
    ODP:ok

68. Otwarcie naboru powiadamia obserwujących obszar?
    Propozycja: tak
    ODP:ok

## J. Pośrednik innowacji

69. Wejście: typ instytucji, grupa, skala, budżet — coś jeszcze?
    Propozycja: + powiat + krótki opis problemu
    ODP:ok

70. Bez AI: szablon karty + najlepiej dopasowana innowacja z Biblioteki?
    Propozycja: tak
    ODP:ok

71. „Koszty bez wymyślonych kwot” — jak?
    Propozycja: tylko kategorie kosztów, bez liczb
    ODP:ok

72. Kartę usługi można zapisać/wydrukować?
    Propozycja: zapis + print
    ODP:ok

73. Źródła finansowania: fikcyjne czy realne nazwy programów (FEM, PFRON…)?
    Propozycja: realne ogólne nazwy + „sprawdź aktualne nabory”
    ODP:ok

## K. Dane i prywatność

74. Maskowanie: PESEL (z sumą kontrolną), telefon, e-mail, adres, imię po „syn/córka/mąż…”?
    Propozycja: tak, PESEL z walidacją sumy
    ODP:ok

75. Maskować też nazwiska lekarzy/placówek?
    Propozycja: placówek nie, „dr X” tak
    ODP:ok

76. Pokazać użytkownikowi, co zamaskowano, przed zapisem?
    Propozycja: tak, podgląd „tak zapiszemy”
    ODP:ok

77. Zapisujemy gdziekolwiek oryginał?
    Propozycja: nigdy — maskowanie przed DB i AI
    ODP:ok

78. Retencja danych w docs (np. 24 mies.)?
    Propozycja: tak
    ODP:ok

79. RODO (administrator, podstawa prawna) tylko w docs?
    Propozycja: tak, krótko
    ODP:ok

80. Kto sprawdza, że seedy nie przypominają prawdziwych osób?
    Propozycja: ja + Twój rzut oka
    ODP:ok

## L. AI

81. Model: Haiku 4.5 (claude-haiku-4-5-20251001)?
    Propozycja: tak
    ODP:ok

82. ⚡ Masz klucz API na demo? Jaki budżet?
    Propozycja: ?
    ODP:mam,kilka dolarów

83. Timeout → fallback na szablon po ilu sekundach?
    Propozycja: 8 s
    ODP:ok

84. Oznaczenie AI w UI?
    Propozycja: miętowa ramka + „Wygenerowane przez AI — sprawdź”
    ODP:ok

85. AI w matchmakingu: rozszerza zapytanie czy tylko podsumowuje?
    Propozycja: rozszerza słowa kluczowe; ranking dalej BM25
    ODP:ok

86. W demo/filmie wersja z AI czy bez?
    Propozycja: z AI; w README zrzut obu
    ODP:ok

## M. WCAG

87. A+ i wysoki kontrast zapamiętywane w cookie (działa bez JS)?
    Propozycja: tak
    ODP:ok

88. Pełne działanie bez JS?
    Propozycja: tak, JS tylko jako ulepszenie
    ODP:ok

89. axe-core (Playwright): w pytest czy osobny skrypt?
    Propozycja: osobny skrypt + raport w docs/WCAG
    ODPok
90. Test z czytnikiem ekranu (NVDA)?
    Propozycja: szybki ręczny test strony głównej, jeśli czas
    ODP:ok

## N. Wygląd i marka

91. Logo SVG — splecione nici w serce/objęcie?
    Propozycja: tak, prosty geometryczny węzeł
    ODP:ok

92. Fonty: systemowe czy self-hosted (Atkinson Hyperlegible)?
    Propozycja: Atkinson Hyperlegible self-hosted
    ODP:ok

93. Kolory nici: 7 obszarów, kontrast do kremu?
    Propozycja: tak + wzór/ikona (nie tylko kolor)
    ODP:ok

## O. Stos i deploy

94. ⚡ Masz Coolify na Hetznerze + wolną domenę (np. hugme.twapp.pl)?
    Propozycja: ?
    ODP:ok

95. SQLite w wolumenie Dockera wystarczy na demo?
    Propozycja: tak
    ODP:ok

96. Python 3.12 lokalnie? venv czy uv?
    Propozycja: venv + requirements.txt
    ODP:ok

## P. Oddanie

97. Slajdy: HTML → PDF czy PPTX?
    Propozycja: HTML → PDF (spójne z UI)
    ODP:ok

98. Film: kto nagrywa/montuje, lektor?
    Propozycja: Ty nagrywasz ekran z lektorem; ja piszę scenariusz minuta po minucie
    ODP:ok

99. Język kodu i komentarzy?
    Propozycja: kod po angielsku, UI i docs po polsku
    ODP:ok

100. Licencja repo do czasu odpowiedzi mentorów?
     Propozycja: brak pliku LICENSE + pytanie w PYTANIA_DO_MENTOROW
     ODP:ok

---

## Twoje dodatkowe uwagi / pomysły

-

---

## Decyzje przed oddaniem (3.10.2026 wieczorem, 50 pytań)

1. Przekaz: **obywatel → dopasowanie** („opisz po swojemu → co działa, kto pomoże, skąd pieniądze”); Hub i luki jako drugie zdanie.
2. **AI włączone na demo**, ale z zaporami: maskowanie danych w jednym miejscu dla każdego zapytania, dzienny limit
   `AI_DAILY_LIMIT=300`, limit kwotowy w konsoli; film celowo bez AI – dopasowanie działa i jest wyjaśnialne bez niego.
3. Dane o zdrowiu po maskowaniu nadal są danymi o zdrowiu – w pilotażu o AI decyduje ROPS po DPIA (wariant bez AI pełny).
4. **Publiczne demo (`DEMO_MODE=1`)**: konta z paska demo nie do zablokowania, ramka „Oglądasz demo?” dla jury,
   odnawianie bazy co godzinę, ale tylko po 20 min bez nowych wpisów.
5. Moderacja po publikacji: Hub może **ukryć i przywrócić** pomysł lub wiadomość (z wpisem w dzienniku).
6. Uczciwość materiałów: plakietki PRZYKŁAD, „Typowa sytuacja” zamiast niesprawdzonych liczb, „bez naruszeń
   **wykrywanych automatycznie**” zamiast „zgodne z WCAG”, nagłówek „Rozwiązania z Biblioteki Innowacji”.
7. Audyt dostępności w CI blokuje scalenie; dodatkowo kontrola układu na telefonie z A+ na każdym widoku.
8. Film: napisy PL wtopione w obraz, plansza końcowa z adresami, lektor z syntezatora.
9. Bez pliku LICENSE do decyzji właściciela praw; docelowo EUPL 1.2.
