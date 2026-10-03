"""Treści przykładowe (FIKCYJNE). Organizacje mają dopisek „(PRZYKŁAD)” – w UI dodatkowo plakietka."""

# (name, role, org, areas, bio, is_demo)
USERS = [
    ("Anna – mama, powiat wadowicki", "mieszkaniec", None, "rodziny-zd", "", 1),
    ("Marta – Fundacja Razem Bliżej", "ngo", "Fundacja Razem Bliżej (PRZYKŁAD)", "rodziny-zd,samotnosc", "", 1),
    ("Piotr – Urząd Gminy Przykładowo", "gmina", "Gmina Przykładowo (PRZYKŁAD)", "seniorzy,wies", "", 1),
    ("Ewa – ekspertka ds. integracji", "ekspert", "Niezależna ekspertka (PRZYKŁAD)", "rodziny-zd,psychiczne",
     "Pedagożka specjalna. Pomaga szkołom i rodzicom w integracji dzieci z zespołem Downa, "
     "doradza przy organizacji grup wsparcia dla rodziców.", 1),
    ("Joanna – koordynatorka Hubu ROPS", "admin", "ROPS Kraków – Hub Innowacji Społecznych", "", "", 1),
    # Eksperci spoza kont demo – pojawiają się w dopasowaniach.
    ("Tomasz – trener pracy wspomaganej", "ekspert", "Spółdzielnia socjalna (PRZYKŁAD)", "rodziny-zd",
     "Trener pracy. Przygotowuje młodych dorosłych z niepełnosprawnością intelektualną do zatrudnienia, "
     "rozmawia z pracodawcami, prowadzi staże i treningi pracy.", 0),
    ("Katarzyna – psycholożka dzieci i młodzieży", "ekspert", "Poradnia (PRZYKŁAD)", "psychiczne,rodziny-zd",
     "Psycholożka. Pracuje z nastolatkami w kryzysie i z rodzicami zmęczonymi długą opieką. "
     "Prowadzi grupy wsparcia dla opiekunów.", 0),
    ("Jan – doradca transportu lokalnego", "ekspert", "Niezależny doradca (PRZYKŁAD)", "wies,seniorzy",
     "Pomaga gminom uruchomić bus na telefon i dowozy do lekarza w małych miejscowościach.", 0),
    ("Agnieszka – animatorka senioralna", "ekspert", "Klub seniora (PRZYKŁAD)", "seniorzy,samotnosc",
     "Animatorka. Zakłada kluby seniora i sąsiedzkie spotkania, przeciwdziała samotności osób starszych.", 0),
    ("Michał – trener kompetencji cyfrowych", "ekspert", "Biblioteka (PRZYKŁAD)", "cyfrowe,seniorzy",
     "Uczy seniorów obsługi smartfona, profilu zaufanego, e-recepty i bezpiecznego internetu.", 0),
    ("Ola – specjalistka partnerstw lokalnych", "ekspert", "Niezależna ekspertka (PRZYKŁAD)", "wspolpraca",
     "Łączy gminy, organizacje i firmy w partnerstwa, pomaga pisać wnioski o granty.", 0),
]

# (title, summary, description, area, powiat, stage, audience, org, keywords)
INNOVATIONS = [
    ("Asystent zdrowia rodziny",
     "Jedna osoba umawia i układa wizyty dziecka u wielu specjalistów.",
     "Asystent zdrowia prowadzi wspólny kalendarz wizyt u kardiologa, logopedy, endokrynologa i innych "
     "lekarzy. Pilnuje terminów, skierowań i wyników badań, żeby rodzice nie musieli robić tego sami.",
     "rodziny-zd", "wadowicki", "wdrożenie", "rodzice i opiekunowie", "Stowarzyszenie Krok Dalej (PRZYKŁAD)",
     "koordynacja wizyt kalendarz specjaliści lekarze terminy zespół Downa"),
    ("Dzień Specjalistów w jednym miejscu",
     "Raz w miesiącu kilku lekarzy przyjmuje dzieci w jednym budynku, jednego dnia.",
     "Centrum usług społecznych zaprasza kardiologa, logopedę, okulistę i fizjoterapeutę na jeden dzień. "
     "Rodzina przyjeżdża raz zamiast pięć razy. Mniej dojazdów, mniej zwolnień z pracy.",
     "rodziny-zd", "myślenicki", "test", "rodzice i opiekunowie", "CUS Myślenice (PRZYKŁAD)",
     "wizyty lekarze specjaliści jeden dzień przychodnia dojazd niepełnosprawność"),
    ("Godziny dla rodzica – opieka wytchnieniowa",
     "Przeszkolony opiekun zostaje z dzieckiem, a rodzic może odpocząć.",
     "Rodzice dzieci z niepełnosprawnością dostają kilka godzin w tygodniu wytchnienia. Opiekunowie "
     "przechodzą szkolenie, a pierwsze spotkanie odbywa się razem z rodzicem.",
     "rodziny-zd", "krakowski", "wdrożenie", "rodzice i opiekunowie", "Fundacja Razem Bliżej (PRZYKŁAD)",
     "odciążenie odpoczynek zmęczenie opieka wytchnieniowa rodzice wsparcie"),
    ("Klub Rodziców i Rodzeństwa",
     "Comiesięczne spotkania rodzin – rozmowa, porady i zajęcia dla rodzeństwa.",
     "Rodzice wymieniają się doświadczeniem i kontaktami do sprawdzonych specjalistów. W tym czasie "
     "rodzeństwo ma własne zajęcia. Spotkania prowadzi psycholog.",
     "rodziny-zd", "Kraków", "wdrożenie", "rodzice i opiekunowie", "Stowarzyszenie Razem z Down (PRZYKŁAD)",
     "grupa wsparcia rodzice rodzeństwo spotkania rozmowa zmęczenie"),
    ("Kawiarnia Treningowa „Po Szkole”",
     "Młodzi dorośli z zespołem Downa uczą się pracy w prawdziwej kawiarni.",
     "Po skończeniu szkoły uczestnicy przechodzą roczny trening pracy: obsługa gości, kasa, kuchnia. "
     "Trener pracy pomaga potem znaleźć zatrudnienie u lokalnych pracodawców.",
     "rodziny-zd", "Nowy Sącz", "wdrożenie", "dorośli", "Spółdzielnia Socjalna Filiżanka (PRZYKŁAD)",
     "praca po szkole zatrudnienie dorosłość trening pracy kawiarnia samodzielność"),
    ("Klasa w Ruchu – integracja od pierwszego dnia",
     "Warsztaty dla całej klasy i wsparcie nauczyciela, gdy do szkoły przychodzi dziecko z zespołem Downa.",
     "Przed rozpoczęciem roku klasa poznaje nowego kolegę przez zabawę. Nauczyciel dostaje konsultacje, "
     "a rodzice – kontakt do asystenta ucznia.",
     "rodziny-zd", "tarnowski", "test", "dzieci i młodzież", "Fundacja Szkoła dla Wszystkich (PRZYKŁAD)",
     "szkoła integracja klasa rówieśnicy nauczyciel asystent ucznia"),
    ("Mapa Wsparcia Rodzin",
     "Jedno miejsce z ofertami pomocy w powiecie: terapie, turnusy, ulgi i świadczenia.",
     "Prosta lista sprawdzonych ofert pomocy dla rodzin osób z niepełnosprawnością, aktualizowana przez "
     "organizacje i gminy. Każda oferta ma kontakt i informację, jak się zapisać.",
     "rodziny-zd", "chrzanowski", "prototyp", "rodzice i opiekunowie", "Powiatowe Centrum Pomocy (PRZYKŁAD)",
     "oferty pomocy informacja ulgi świadczenia turnusy terapie gdzie szukać"),
    ("Dzienny Dom Seniora w remizie",
     "Remiza OSP otwiera się dla seniorów w dni powszednie.",
     "Strażacy-ochotnicy i koło gospodyń prowadzą zajęcia, wspólny obiad i gimnastykę. Senior nie "
     "musi jechać do miasta, żeby mieć towarzystwo i opiekę.",
     "seniorzy", "limanowski", "wdrożenie", "seniorzy", "OSP Przykładowa Wieś (PRZYKŁAD)",
     "seniorzy opieka dzienna wieś remiza towarzystwo obiad"),
    ("Asystent Seniora na telefon",
     "Asystent pomaga starszej osobie w drodze do lekarza, urzędu i na zakupy.",
     "Senior dzwoni dzień wcześniej, a asystent przyjeżdża i towarzyszy w sprawach poza domem. "
     "Usługa działa w gminie razem z ośrodkiem pomocy społecznej.",
     "seniorzy", "bocheński", "wdrożenie", "seniorzy", "Gmina Przykładowo (PRZYKŁAD)",
     "asystent senior wizyta lekarz zakupy urząd towarzyszenie"),
    ("Złota Rączka dla Seniora",
     "Bezpłatne drobne naprawy w mieszkaniach osób starszych.",
     "Wolontariusze i firmy z okolicy naprawiają kran, wymieniają żarówki i montują uchwyty. "
     "Przy okazji sprawdzają, czy mieszkanie jest bezpieczne.",
     "seniorzy", "olkuski", "wdrożenie", "seniorzy", "Fundacja Pomocna Dłoń (PRZYKŁAD)",
     "naprawy dom senior bezpieczeństwo wolontariat firmy"),
    ("Sąsiedzka Koperta Życia",
     "Informacja o zdrowiu w lodówce i sąsiad, który wie, gdy coś się dzieje.",
     "Senior trzyma kartę z lekami i kontaktami w lodówce. Sąsiedzi zgłaszają się jako „zaufani” "
     "i odwiedzają osobę raz w tygodniu.",
     "seniorzy", "gorlicki", "test", "seniorzy", "Klub Seniora Pogodna Jesień (PRZYKŁAD)",
     "senior bezpieczeństwo sąsiad zdrowie leki samotnie"),
    ("Telefon Życzliwości",
     "Wolontariusze dzwonią do samotnych osób na rozmowę.",
     "Raz lub dwa razy w tygodniu przeszkolony wolontariusz dzwoni, pyta, jak minął dzień, i słucha. "
     "Gdy trzeba, przekazuje informację do ośrodka pomocy.",
     "samotnosc", "Tarnów", "wdrożenie", "seniorzy", "Fundacja Głos Serca (PRZYKŁAD)",
     "samotność rozmowa telefon wolontariusz kontakt seniorzy"),
    ("Międzypokoleniowe Podwórko",
     "Młodzież i seniorzy razem prowadzą ogród na osiedlu.",
     "Wspólne grządki, ławki i kawa w każdą sobotę. Starsi uczą sadzenia, młodsi pomagają w cięższych "
     "pracach. Na osiedlu znika anonimowość.",
     "samotnosc", "oświęcimski", "wdrożenie", "cała społeczność", "Stowarzyszenie Zielone Osiedle (PRZYKŁAD)",
     "samotność sąsiedzi ogród młodzież seniorzy więzi spotkania"),
    ("Stół Sąsiedzki",
     "Raz w miesiącu wspólna kolacja dla wszystkich mieszkańców ulicy.",
     "Każdy przynosi coś do jedzenia. Spotkania organizują sami sąsiedzi, a gmina użycza świetlicy. "
     "Przychodzą też osoby, które mieszkają same.",
     "samotnosc", "wielicki", "pomysł", "cała społeczność", "Grupa Sąsiedzka (PRZYKŁAD)",
     "sąsiedzi samotność spotkania kolacja więzi świetlica"),
    ("Cyfrowy Przewodnik w bibliotece",
     "Licealiści uczą seniorów obsługi smartfona i spraw przez internet.",
     "Spotkania jeden na jeden: e-recepta, profil zaufany, mObywatel, rozmowa wideo z wnukami. "
     "Uczniowie dostają zaświadczenie o wolontariacie.",
     "cyfrowe", "nowotarski", "wdrożenie", "seniorzy", "Biblioteka Gminna (PRZYKŁAD)",
     "smartfon internet seniorzy e-recepta profil zaufany nauka wolontariat"),
    ("Tablet z Bibliotecznej Półki",
     "Wypożyczalnia tabletów z gotowymi aplikacjami i krótkim szkoleniem.",
     "Osoby bez sprzętu wypożyczają tablet na miesiąc. Na start dostają instrukcję dużą czcionką "
     "i numer do konsultanta.",
     "cyfrowe", "suski", "test", "seniorzy", "Biblioteka Publiczna (PRZYKŁAD)",
     "tablet sprzęt wypożyczalnia internet aplikacje seniorzy"),
    ("Punkt e-Spraw w sołectwie",
     "Dyżur w świetlicy: pomoc przy formularzach i sprawach online.",
     "Raz w tygodniu pracownik gminy pomaga wypełnić wnioski przez internet, założyć konto w banku "
     "i sprawdzić termin u lekarza.",
     "cyfrowe", "miechowski", "wdrożenie", "dorośli", "Gmina Przykładowo (PRZYKŁAD)",
     "e-sprawy formularz wniosek internet wieś pomoc online"),
    ("Szkolny Punkt Pierwszego Kontaktu",
     "Psycholog w szkole bez zapisów i bez kolejki.",
     "Uczeń może przyjść na przerwie i porozmawiać. Psycholog ocenia, czy potrzebna jest dalsza pomoc, "
     "i pomaga rodzicom znaleźć terapię.",
     "psychiczne", "Kraków", "wdrożenie", "dzieci i młodzież", "Fundacja Spokojna Głowa (PRZYKŁAD)",
     "psycholog szkoła młodzież kryzys rozmowa nastolatki emocje"),
    ("Krąg Opiekunów",
     "Grupa wsparcia dla osób, które długo opiekują się bliskim.",
     "Spotkania na żywo i online prowadzone przez psychologa. Uczestnicy uczą się dbać o siebie "
     "i rozpoznawać wypalenie.",
     "psychiczne", "nowosądecki", "test", "rodzice i opiekunowie", "Stowarzyszenie Opiekun (PRZYKŁAD)",
     "opiekunowie wypalenie zmęczenie wsparcie psycholog grupa rodzice"),
    ("Przyjaciel na Ławce",
     "Przeszkoleni wolontariusze rozmawiają z osobami w trudnym momencie.",
     "W parku i przy bibliotece stoją oznaczone ławki. W stałych godzinach dyżuruje tam wolontariusz, "
     "który wysłucha i pokaże, gdzie szukać pomocy.",
     "psychiczne", "brzeski", "prototyp", "dorośli", "Fundacja Głos Serca (PRZYKŁAD)",
     "rozmowa kryzys wsparcie emocje wolontariusz samotność"),
    ("Bus na Telefon",
     "Gminny bus przyjeżdża na zamówienie – do lekarza, urzędu, szkoły.",
     "Mieszkańcy zamawiają kurs telefonicznie dzień wcześniej. Bus łączy kilka wsi i jeździ tam, "
     "gdzie nie ma autobusu.",
     "wies", "dąbrowski", "wdrożenie", "cała społeczność", "Gmina Przykładowo (PRZYKŁAD)",
     "transport dojazd dojechać bus wieś sołectwa przychodnia lekarz autobus na żądanie starsi mieszkańcy"),
    ("Sąsiedzkie Dojazdy",
     "Mieszkańcy dzielą się miejscami w samochodach jadących do miasta.",
     "Prosta tablica w sklepie i grupa telefoniczna: kto jedzie, dokąd i o której. Gmina ubezpiecza "
     "kierowców-wolontariuszy.",
     "wies", "proszowicki", "pomysł", "cała społeczność", "Koło Gospodyń Wiejskich (PRZYKŁAD)",
     "dojazd samochód sąsiedzi wieś transport do lekarza"),
    ("Gminne Laboratorium Innowacji",
     "Gmina, organizacje, firmy i mieszkańcy razem projektują nowe usługi.",
     "Cztery warsztaty w roku według metody design thinking. Najlepsze pomysły dostają mały grant "
     "na test i wsparcie Hubu.",
     "wspolpraca", "wadowicki", "wdrożenie", "cała społeczność", "Gmina Przykładowo (PRZYKŁAD)",
     "współpraca gmina organizacje firmy partnerstwo warsztaty grant"),
    ("Inkubator Partnerstw dla NGO",
     "Łączymy organizacje z firmami, które chcą pomagać.",
     "Organizacja opisuje potrzebę, firma – zasoby (ludzi, sprzęt, pieniądze). Moderator dobiera pary "
     "i pomaga podpisać porozumienie.",
     "wspolpraca", "Kraków", "test", "cała społeczność", "Fundacja Most (PRZYKŁAD)",
     "partnerstwo organizacje firmy wolontariat pracowniczy współpraca"),
]

# (body, area, powiat, days_ago, status, approved)
REPORTS = [
    ("Rodzice dzieci z zespołem Downa w naszej gminie jeżdżą do wielu lekarzy w różnych miastach. Każda wizyta to inny dzień i zwolnienie z pracy.",
     "rodziny-zd", "wadowicki", 3, "nowe", 0),
    ("Brakuje informacji, gdzie szukać terapii i turnusów dla dzieci z niepełnosprawnością. Każdy rodzic szuka sam.",
     "rodziny-zd", "chrzanowski", 9, "polaczone", 1),
    ("Młodzi dorośli z zespołem Downa po skończeniu szkoły siedzą w domu. Nie ma dla nich pracy ani zajęć.",
     "rodziny-zd", "Nowy Sącz", 15, "w-analizie", 1),
    ("Rodzice dzieci z niepełnosprawnością są bardzo zmęczeni. Nie mają nikogo, kto zostałby z dzieckiem choć na kilka godzin.",
     "rodziny-zd", "krakowski", 22, "polaczone", 1),
    ("W szkole naszych dzieci nauczyciele nie wiedzą, jak pomóc w integracji ucznia z zespołem Downa z klasą.",
     "rodziny-zd", "tarnowski", 34, "polaczone", 1),
    ("Brakuje mieszkań treningowych, w których dorośli z niepełnosprawnością intelektualną mogliby uczyć się samodzielnego życia.",
     "rodziny-zd", "Kraków", 41, "luka", 1),
    ("Dorośli z zespołem Downa nie mają gdzie pływać – na basenie brakuje instruktora i zajęć dla nich.",
     "rodziny-zd", "myślenicki", 58, "luka", 1),
    ("Starsi mieszkańcy naszych wsi nie mają jak dojechać do przychodni, autobus jeździ dwa razy dziennie.",
     "wies", "dąbrowski", 5, "nowe", 0),
    ("Seniorzy mieszkający samotnie w bloku nie mają z kim porozmawiać, rodziny są daleko.",
     "samotnosc", "Tarnów", 12, "polaczone", 1),
    ("Osoby starsze nie umieją umówić się do lekarza przez internet i nie wiedzą, co to e-recepta.",
     "cyfrowe", "nowotarski", 19, "polaczone", 1),
    ("Młodzież w naszej szkole przeżywa kryzysy, a na psychologa czeka się kilka miesięcy.",
     "psychiczne", "Kraków", 27, "w-analizie", 1),
    ("Opiekunowie osób leżących są wypaleni i nie mają wsparcia psychologicznego.",
     "psychiczne", "nowosądecki", 46, "polaczone", 1),
    ("W naszej gminie organizacje i urząd działają osobno, nikt nie wie, kto co robi.",
     "wspolpraca", "wadowicki", 63, "polaczone", 1),
    ("Seniorzy w małych miejscowościach nie mają gdzie spędzać dnia, brakuje dziennej opieki.",
     "seniorzy", "limanowski", 71, "polaczone", 1),
    ("Starsze osoby mieszkające same boją się, że nikt nie zauważy, gdy zasłabną w domu.",
     "seniorzy", "gorlicki", 80, "w-analizie", 1),
    ("Na osiedlu ludzie się nie znają, nowi mieszkańcy czują się samotni.",
     "samotnosc", "oświęcimski", 88, "polaczone", 1),
    ("Mieszkańcy wsi bez samochodu nie dojadą do pracy w mieście, nie ma porannego kursu.",
     "wies", "proszowicki", 95, "w-analizie", 1),
    ("Seniorzy nie mają sprzętu – komputera ani tabletu – żeby rozmawiać z rodziną przez internet.",
     "cyfrowe", "suski", 101, "polaczone", 1),
    ("Brakuje dentysty, który przyjmuje dorosłe osoby z niepełnosprawnością intelektualną w znieczuleniu ogólnym.",
     "rodziny-zd", "gorlicki", 108, "luka", 1),
    ("Rodzice nastolatków z zespołem Downa szukają miejsc, gdzie ich dzieci mogą spotykać rówieśników po lekcjach.",
     "rodziny-zd", "bocheński", 113, "w-analizie", 1),
    ("Starsi mieszkańcy nie radzą sobie z drobnymi naprawami w domu, a fachowcy nie chcą przyjeżdżać do małych zleceń.",
     "seniorzy", "olkuski", 117, "polaczone", 1),
    ("Firmy z naszego powiatu chciałyby pomagać, ale nie wiedzą, którym organizacjom i jak.",
     "wspolpraca", "Kraków", 119, "zamkniete", 1),
    # Skupiska do trendów: rodziny-zd rośnie w ostatnich 30 dniach (wadowicki, krakowski, myślenicki),
    # seniorzy i transport w powiatach wiejskich, zdrowie psychiczne młodzieży w Krakowie.
    ("Rodzice dzieci z zespołem Downa z kilku wsi dojeżdżają do specjalistów nawet 60 kilometrów, często kilka razy w miesiącu.",
     "rodziny-zd", "wadowicki", 2, "nowe", 0),
    ("W naszej gminie rodzice dzieci z niepełnosprawnością nie mają z kim zostawić dziecka, gdy sami muszą iść do lekarza.",
     "rodziny-zd", "wadowicki", 6, "w-analizie", 1),
    ("Rodziny dzieci z zespołem Downa gubią się w terminach wizyt i skierowaniach – każda przychodnia ma inny system zapisów.",
     "rodziny-zd", "wadowicki", 11, "polaczone", 1),
    ("Brakuje grupy wsparcia dla rodziców, którzy dopiero usłyszeli diagnozę zespołu Downa u dziecka.",
     "rodziny-zd", "wadowicki", 17, "polaczone", 1),
    ("Rodzice dzieci z zespołem Downa są przemęczeni opieką i nie mają nawet kilku godzin odpoczynku w tygodniu.",
     "rodziny-zd", "krakowski", 4, "nowe", 0),
    ("Nauczyciele w szkołach w naszym powiecie nie mają wsparcia, gdy do klasy trafia uczeń z zespołem Downa.",
     "rodziny-zd", "krakowski", 9, "w-analizie", 1),
    ("Młodzi dorośli z niepełnosprawnością intelektualną po szkole nie mają zajęć ani pracy w okolicy.",
     "rodziny-zd", "krakowski", 25, "polaczone", 1),
    ("Rodzice dzieci z zespołem Downa nie wiedzą, jakie ulgi i świadczenia im przysługują i gdzie o nie pytać.",
     "rodziny-zd", "myślenicki", 7, "polaczone", 1),
    ("Dzieci z zespołem Downa czekają miesiącami na logopedę i rehabilitację w naszym powiecie.",
     "rodziny-zd", "myślenicki", 14, "w-analizie", 1),
    ("Seniorzy z małych sołectw nie mają jak dojechać do przychodni, a gminny bus jeździ tylko z dziećmi do szkoły.",
     "wies", "dąbrowski", 3, "nowe", 0),
    ("Starsze osoby mieszkające samotnie na wsi nie mają kto im pomóc w zakupach i drobnych sprawach.",
     "seniorzy", "dąbrowski", 13, "w-analizie", 1),
    ("Mieszkańcy kilku wsi bez samochodu nie dojadą do urzędu i apteki, ostatni autobus odjeżdża przed południem.",
     "wies", "dąbrowski", 21, "polaczone", 1),
    ("Seniorzy w górskich wsiach całymi dniami są sami, brakuje miejsca, gdzie mogliby się spotykać.",
     "seniorzy", "limanowski", 10, "w-analizie", 1),
    ("Starsze osoby po wyjściu ze szpitala wracają do domu bez żadnej opieki i wsparcia sąsiadów.",
     "seniorzy", "limanowski", 28, "polaczone", 1),
    ("Uczniowie szkół średnich coraz częściej mają ataki lęku przed lekcjami, a szkolny psycholog jest raz w tygodniu.",
     "psychiczne", "Kraków", 5, "nowe", 0),
    ("Nastolatki po kryzysie psychicznym wracają do szkoły i nie mają żadnego wsparcia w klasie.",
     "psychiczne", "Kraków", 12, "w-analizie", 1),
    ("Rodzice nastolatków w kryzysie nie wiedzą, gdzie szybko szukać pomocy, a terminy u psychiatry są odległe.",
     "psychiczne", "Kraków", 19, "polaczone", 1),
    ("Seniorzy w naszej gminie dostają SMS-y od oszustów i boją się korzystać z bankowości w telefonie.",
     "cyfrowe", "nowotarski", 8, "w-analizie", 1),
    ("Osoby starsze nie potrafią założyć profilu zaufanego i załatwić sprawy w urzędzie przez internet.",
     "cyfrowe", "nowotarski", 26, "polaczone", 1),
    ("Starsi mieszkańcy bloków w centrum miasta nie znają sąsiadów i nie mają z kim porozmawiać.",
     "samotnosc", "Tarnów", 16, "polaczone", 1),
]

# (title, area, kind, summary, body)
MATERIALS = [
    ("Jak przygotować się do wizyty u specjalisty", "rodziny-zd", "lista kontrolna",
     "Krótka lista: co zabrać i o co zapytać lekarza, żeby wizyta dała jak najwięcej.",
     "Przed wizytą zapisz w punktach, co się zmieniło od ostatniego razu.\n\nZabierz: skierowanie, wyniki "
     "ostatnich badań, listę leków, zeszyt z notatkami.\n\nZapytaj: co dalej, kiedy kontrola, jakie objawy "
     "powinny mnie zaniepokoić, kto może pomóc między wizytami.\n\nPo wizycie wpisz zalecenia do wspólnego "
     "kalendarza rodziny."),
    ("Gdzie szukać pomocy dla rodziny dziecka z niepełnosprawnością", "rodziny-zd", "poradnik",
     "Mapa instytucji: kto za co odpowiada i od czego zacząć.",
     "Ośrodek pomocy społecznej (OPS lub CUS) – pierwsze miejsce, gdzie zapytasz o wsparcie w gminie.\n\n"
     "Powiatowe centrum pomocy rodzinie – dofinansowania, turnusy rehabilitacyjne.\n\nPoradnia "
     "psychologiczno-pedagogiczna – opinie i orzeczenia dla szkoły.\n\nOrganizacje rodziców – "
     "najwięcej praktycznej wiedzy i wsparcia. Sprawdź aktualne zasady w swojej gminie."),
    ("Ścieżka rodziny: od diagnozy do dorosłości", "rodziny-zd", "poradnik",
     "Cztery etapy i to, co warto wiedzieć na każdym z nich.",
     "To ogólny przewodnik, nie porada medyczna. Szczegóły zawsze omawiaj z lekarzem i specjalistami."),
    ("Jak opisać pomysł na innowację społeczną", "wspolpraca", "instrukcja",
     "Cztery pytania, od których zaczyna się każdy dobry pomysł.",
     "1. Jaki problem rozwiązujesz – i skąd wiesz, że istnieje?\n2. Dla kogo jest rozwiązanie?\n"
     "3. Co jest nowego w Twoim podejściu?\n4. Jak sprawdzisz, że działa?\n\nZacznij od fiszki w Kreatorze "
     "pomysłów – zajmie Ci to 5 minut."),
    ("Bezpieczny smartfon – poradnik dla seniorów", "cyfrowe", "poradnik",
     "Jak rozpoznać oszustwo i bezpiecznie korzystać z telefonu.",
     "Bank nigdy nie prosi o hasło przez telefon.\n\nNie klikaj w linki z SMS-ów o dopłacie do paczki.\n\n"
     "Ustaw większą czcionkę: Ustawienia → Wyświetlacz → Rozmiar czcionki.\n\nW razie wątpliwości "
     "zadzwoń do kogoś bliskiego, zanim cokolwiek zrobisz."),
    ("Jak założyć grupę wsparcia", "psychiczne", "instrukcja",
     "Od pierwszego spotkania do stałej grupy – krok po kroku.",
     "Znajdź salę (świetlica, biblioteka, parafia). Ustal stały termin. Poproś psychologa o poprowadzenie "
     "pierwszych spotkań.\n\nZasady grupy: poufność, mówimy o sobie, nikt nie musi mówić.\n\nOgłoś "
     "spotkanie w OPS, szkole i przychodni."),
    ("Transport na żądanie – jak zacząć w gminie", "wies", "instrukcja",
     "Pierwsze kroki: potrzeby, trasa, budżet, zapisy.",
     "Policz, ile osób potrzebuje dowozu i dokąd. Sprawdź, czy gmina ma pojazd (np. bus szkolny w "
     "godzinach poza dowozem dzieci). Ustal zapisy telefoniczne dzień wcześniej. Po trzech miesiącach "
     "zbierz opinie i popraw rozkład."),
    ("Samotność w mieście – małe kroki, które działają", "samotnosc", "poradnik",
     "Pomysły sąsiedzkie, które nic nie kosztują.",
     "Tablica ogłoszeń na klatce. Wspólne sprzątanie podwórka. Lista „chętnie pomogę” – kto może zrobić "
     "zakupy, kto pożyczy wiertarkę. Najważniejsze jest pierwsze zaproszenie."),
]

# (title, area, description, is_open, deadline)
CALLS = [
    ("Małopolskie Innowacje Społeczne 2026 – odciążenie opiekunów", "rodziny-zd",
     "Granty na przetestowanie nowych usług, które dają opiekunom osób z niepełnosprawnością czas na odpoczynek.",
     1, "2026-11-15"),
    ("Transport w małych miejscowościach", "wies",
     "Wsparcie dla gmin i organizacji testujących dowozy na żądanie i sąsiedzkie dojazdy.",
     1, "2026-12-01"),
    ("Seniorzy w sieci", "cyfrowe",
     "Nabór zakończony. Wspierał naukę kompetencji cyfrowych osób starszych.",
     0, "2026-06-30"),
]

# (user_index, title, essence, audience, stage, area, canvas)
IDEAS = [
    (1, "Weekendowy klub dla nastolatków z zespołem Downa",
     "Sobotnie spotkania z rówieśnikami: gry, gotowanie, wyjścia do miasta. Rodzice mają w tym czasie wolne.",
     "dzieci i młodzież", "prototyp", "rodziny-zd",
     {"problem": "Nastolatki z zespołem Downa nie mają gdzie spotykać rówieśników, a rodzice nie mają chwili dla siebie.",
      "odbiorcy": "Młodzież 13–18 lat i ich rodzice z powiatu krakowskiego.",
      "rozwiazanie": "Klub w sobotę 10–14, prowadzony przez animatora i wolontariuszy.",
      "wartosc": "Przyjaźnie, samodzielność, 4 godziny odpoczynku dla rodziców.",
      "partnerzy": "Szkoła specjalna, dom kultury, harcerze.",
      "zasoby": "Sala, animator, 6 wolontariuszy, materiały do zajęć.",
      "koszty": "Wynagrodzenie animatora, materiały, ubezpieczenie.",
      "mierniki": "Liczba uczestników, frekwencja, ocena rodziców.",
      "ryzyka": "Rotacja wolontariuszy, dojazd uczestników."}),
    (2, "Bus na telefon dla pięciu sołectw",
     "Gmina uruchamia dowóz na żądanie do przychodni i urzędu dla mieszkańców bez samochodu.",
     "cała społeczność", "pomysł", "wies",
     {"problem": "Autobus jeździ dwa razy dziennie, seniorzy nie dojeżdżają do lekarza.",
      "odbiorcy": "Mieszkańcy 5 sołectw, głównie seniorzy."}),
]

# Wątki: (subject_type, subject_key, title, [(user_index, days_ago, body)])
THREADS = [
    ("pomysl", 0, "Pytania do pomysłu: Weekendowy klub",
     [(1, 6, "Czy ktoś ma doświadczenie z ubezpieczeniem wolontariuszy na takich zajęciach?"),
      (3, 5, "Tak – warto mieć umowę wolontariacką i polisę NNW. Chętnie podeślę wzór porozumienia ze szkołą."),
      (4, 4, "Hub może połączyć Was z Klubem Rodziców i Rodzeństwa z Krakowa – robią podobne zajęcia.")]),
    ("pomysl", 1, "Pytania do pomysłu: Bus na telefon",
     [(2, 3, "Od czego zacząć – kupić bus czy wykorzystać szkolny?"),
      (7, 2, "Najpierw zbadajcie potrzeby i sprawdźcie bus szkolny w godzinach 9–13. Zakup to dopiero drugi krok.")]),
    ("zgloszenie", 1, "Zgłoszenie: informacja o terapiach i turnusach",
     [(0, 9, "Zgłaszam w imieniu rodziców z naszej gminy."),
      (4, 8, "Dziękujemy! Połączyliśmy zgłoszenie z innowacją „Mapa Wsparcia Rodzin”. Organizacja z powiatu chrzanowskiego chętnie podzieli się wzorem.")]),
]

# ── Moduł „Razem z ZD” ──────────────────────────────────────────────────────────
# (user_index, kind, powiat, stage, alias, title, body, status, days_ago)
RAZEM_REQUESTS = [
    (0, "przewodnik-szukam", "wadowicki", "przedszkole", "Mama Ani", "",
     "Córka zaczyna przedszkole. Chcę porozmawiać z rodzicem, który ma to za sobą.", "nowe", 2),
    (6, "przewodnik-szukam", "krakowski", "diagnoza", "Tata z Krzeszowic", "",
     "Kilka tygodni temu usłyszeliśmy diagnozę. Szukamy rodziny, która pokaże, od czego zacząć.", "nowe", 5),
    (1, "przewodnik-oferuje", "wadowicki", "przedszkole", "Marta", "",
     "Mój syn skończył przedszkole integracyjne. Chętnie opowiem, jak przygotować dziecko i kadrę.", "nowe", 20),
    (5, "przewodnik-oferuje", "krakowski", "doroslosc", "Tomek", "",
     "Córka pracuje w kawiarni treningowej. Pomogę zaplanować czas po szkole.", "nowe", 40),
    (8, "przewodnik-oferuje", "myślenicki", "szkola", "Agnieszka", "",
     "Przeszliśmy przez szkołę ogólnodostępną z asystentem. Podzielę się doświadczeniem.", "nowe", 33),
    (0, "wytchnienie", "wadowicki", "przedszkole", "Mama Ani", "Sobota, 4 godziny",
     "Potrzebuję kilku godzin w sobotę, żeby załatwić sprawy i odpocząć.", "nowe", 1),
    (0, "dzien-specjalistow", "wadowicki", None, "Mama Ani", "", "", "nowe", 3),
    (1, "dzien-specjalistow", "wadowicki", None, "Marta", "", "", "nowe", 9),
    (2, "dzien-specjalistow", "krakowski", None, "Rodzic z Liszek", "", "", "nowe", 6),
    (6, "dzien-specjalistow", "krakowski", None, "Tata z Krzeszowic", "", "", "nowe", 4),
    (7, "dzien-specjalistow", "myślenicki", None, "Rodzina z Dobczyc", "", "", "nowe", 12),
    (8, "dzien-specjalistow", "nowosądecki", None, "Agnieszka", "", "", "nowe", 15),
    (1, "miejsce", "wadowicki", None, "Marta", "Przychodnia „Pod Lipami” (PRZYKŁAD)",
     "przychodnia: Lekarze mają czas, tłumaczą spokojnie, można umówić kilka wizyt jednego dnia.", "zatwierdzone", 60),
    (0, "miejsce", "wadowicki", None, "Mama Ani", "Gabinet stomatologiczny „Uśmiech” (PRZYKŁAD)",
     "dentysta: Dentystka przyjmuje dzieci z niepełnosprawnością, pierwsza wizyta to oswajanie.", "zatwierdzone", 45),
    (5, "miejsce", "Kraków", None, "Tomek", "Basen „Fala” – zajęcia dla wszystkich (PRZYKŁAD)",
     "basen i sport: Instruktor prowadzi zajęcia dla dorosłych z niepełnosprawnością intelektualną.", "zatwierdzone", 70),
    (8, "miejsce", "myślenicki", None, "Agnieszka", "Fryzjer „Spokojne nożyczki” (PRZYKŁAD)",
     "fryzjer: Cicho, bez pośpiechu, można przyjść wcześniej i obejrzeć salon.", "zatwierdzone", 30),
    (1, "miejsce", "krakowski", None, "Marta", "Kawiarnia „Razem” (PRZYKŁAD)",
     "kawiarnia: Obsługa rozumie potrzeby gości z ZD, menu z obrazkami.", "zatwierdzone", 25),
    (6, "miejsce", "Kraków", None, "Tata z Krzeszowic", "Poradnia rehabilitacyjna „Krok” (PRZYKŁAD)",
     "przychodnia: Rehabilitanci z doświadczeniem z małymi dziećmi z ZD.", "zatwierdzone", 18),
    (0, "miejsce", "wadowicki", None, "Mama Ani", "Plac zabaw „Dla wszystkich” (PRZYKŁAD)",
     "inne: Huśtawki i ścieżki dostępne dla dzieci z różnymi potrzebami.", "nowe", 1),
    (1, "sprzet-oddam", "wadowicki", None, "Marta", "Oddam pionizator dziecięcy (PRZYKŁAD)",
     "Pionizator w dobrym stanie, dla dziecka do ok. 4 lat.", "zatwierdzone", 14),
    (5, "sprzet-oddam", "krakowski", None, "Tomek", "Oddam książki i karty do nauki czytania (PRZYKŁAD)",
     "Komplet kart globalnego czytania i książeczki z obrazkami.", "zatwierdzone", 21),
    (0, "sprzet-przyjme", "wadowicki", None, "Mama Ani", "Przyjmę piłkę rehabilitacyjną (PRZYKŁAD)",
     "Szukamy dużej piłki do ćwiczeń w domu.", "zatwierdzone", 7),
    (8, "sprzet-przyjme", "myślenicki", None, "Agnieszka", "Przyjmę rowerek trójkołowy (PRZYKŁAD)",
     "Dla 7-latka, może być używany.", "zatwierdzone", 11),
]

# (title, powiat, days_from_now, place, body)
RAZEM_EVENTS = [
    ("Piknik rodzin „Razem z ZD” (PRZYKŁAD)", "wadowicki", 9, "Park miejski w Wadowicach",
     "Gry dla dzieci, kawa dla rodziców, rozmowy z rodzicami-przewodnikami."),
    ("Klub rodzeństwa – zajęcia plastyczne (PRZYKŁAD)", "Kraków", 13, "Dom kultury, Kraków",
     "Zajęcia dla braci i sióstr osób z ZD, w tym czasie rodzice mają kawę i rozmowę z psychologiem."),
    ("Spotkanie: jak przygotować się do przedszkola (PRZYKŁAD)", "myślenicki", 18, "Biblioteka w Myślenicach",
     "Rodzice dzielą się doświadczeniem, ekspertka odpowiada na pytania."),
    ("Dzień otwarty kawiarni treningowej (PRZYKŁAD)", "Nowy Sącz", 24, "Kawiarnia „Po Szkole”",
     "Młodzi dorośli z ZD pokazują swoją pracę. Informacje o treningu pracy."),
]
