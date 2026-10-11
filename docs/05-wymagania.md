# 05. Wymagania

Wymagania odtworzone z działającego kodu – każde ma kryterium akceptacji sprawdzalne w aplikacji i wskazanie,
gdzie jest zrealizowane oraz który test go pilnuje. Rzeczy, których aplikacja nie robi, są w
[07-ograniczenia](07-ograniczenia.md), nie tutaj.

Priorytety (MoSCoW) przypisane na podstawie briefu HubMi.pl: matchmaking był modułem obowiązkowym (M), pozostałe moduły
dodatkowe (S), pilotaż „Razem z ZD” to pogłębienie (C).

## Funkcjonalne – matchmaking i zgłoszenia (M)

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-01 | Mieszkaniec opisuje problem własnymi słowami, bez logowania | Gość wpisuje opis 15–1500 znaków i dostaje listę wyników; opis krótszy niż 15 znaków daje komunikat „Napisz trochę więcej…” i kod 422; jedno słowo znane z katalogu (np. „samotność”) wystarcza do szukania | `app/views/public.py` `search`, `validate_search` | `test_matchmaking.py::test_too_short_description_gives_friendly_error` |
| W-02 | Dane osobowe są ukryte, zanim tekst trafi do bazy albo do AI | Opis z PESEL (z poprawną sumą kontrolną), telefonem, e-mailem, adresem, kodem pocztowym, imieniem po „syn/córka” albo nazwiskiem po „dr” zostaje zapisany ze znacznikami `[TELEFON]` itd.; oryginał nie jest zapisywany nigdzie; użytkownik widzi, co ukryto | `core/privacy.py` `mask`, `core/ai.py` `wrap_data` | `test_privacy.py`, `test_ai_bezpieczenstwo.py::test_personal_data_is_masked_for_every_caller` |
| W-03 | Wyniki pokazują dopasowane innowacje z oceną i powodem | Do 5 innowacji z etykietą słowną (≥ 60% „Bardzo pasuje”, ≥ 45% „Pasuje”, ≥ 35% „Może pasować”), procentem, wspólnymi słowami i tematami; ta sama wartość % zawsze daje tę samą etykietę | `core/match.py`, `core/catalog.py` | `test_trafnosc.py::test_explanation_lists_shared_words_and_topics`, `test_same_percent_gives_same_label` |
| W-04 | Trafność wyszukiwania jest mierzona | Na zestawie 16 opisów testowych właściwa innowacja jest w top 3 dla co najmniej 80% przypadków (obecnie 16/16) | `core/match.py` | `test_trafnosc.py::test_hit_at_3_at_least_80_percent`, `test_every_audit_sentence_hits_top_3` |
| W-05 | Gdy nic dobrze nie pasuje, aplikacja mówi to wprost | Przy najlepszym wyniku < 0,35 wyświetla się komunikat o braku sprawdzonego rozwiązania zamiast słabych dopasowań | `core/domain.py` `GAP_THRESHOLD`, szablon `wyniki.html` | `test_matchmaking.py::test_need_without_good_match_says_so_honestly` |
| W-06 | Obok innowacji pokazujemy podobne zgłoszenia, poradniki i ekspertów | Do 3 zatwierdzonych podobnych zgłoszeń, 3 poradników, 3 ekspertów | `core/catalog.py` | `test_matchmaking.py::test_guest_search_shows_explained_matches_and_masks` |
| W-07 | Zgłoszenie zapisuje tylko zalogowany; opis gościa nie ginie | Gość klikający „Zapisz” trafia do wyboru konta; po wyborze wraca do wyników z tym samym opisem | `app/views/public.py` `create_report` | `test_matchmaking.py::test_guest_save_redirects_to_login_and_keeps_draft` |
| W-08 | Zapis zgłoszenia uruchamia obsługę przez Hub | Po zapisie powstaje: zgłoszenie (po maskowaniu), dopasowania, wątek z treścią jako pierwszą wiadomością, powiadomienie i e-mail w kolejce dla każdego administratora | `app/views/public.py` `create_report`, `core/notify.py` | `test_matchmaking.py::test_save_report_masks_creates_thread_and_notifies_admin` |
| W-09 | Zgłoszenie jest prywatne do decyzji Hubu | Niezatwierdzone zgłoszenie widzi tylko autor, Hub i eksperci; inni dostają 403 | `app/views/public.py` `can_see_report` | `test_matchmaking.py::test_unapproved_report_hidden_from_other_users` |
| W-10 | Autor ocenia dopasowania | Tylko autor może oznaczyć dopasowanie jako „pomocne” albo „niepomocne”; ocena zasila miernik trafności w panelu | `app/views/public.py` `rate_match`, `app/views/admin.py` `helpful_rate` | `test_matchmaking.py::test_author_rates_match_and_others_cannot` |
| W-11 | Hub nadaje status i publikuje zgłoszenie | Zmiana statusu albo publikacji wysyła autorowi powiadomienie; brak zmiany – brak powiadomienia | `app/views/admin.py` `set_status` | `test_admin.py::test_status_change_notifies_author` |

## Funkcjonalne – komunikacja (S)

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-12 | Rozmowa w wątku przy zgłoszeniu, pomyśle i innowacji | Wiadomość 2–2000 znaków, maskowana; w wątku zgłoszenia piszą tylko autor, Hub i eksperci | `app/views/komunikacja.py` `post_message`, `can_post` | `test_matchmaking.py::test_stranger_cannot_post_in_report_thread` |
| W-13 | Właściwe osoby dostają powiadomienie | Powiadomienie dostają uczestnicy wątku i autor tematu; Hub – gdy pisze ktoś spoza Hubu; eksperci obszaru – gdy pytanie o pomysł albo innowację zadaje nie-ekspert | `app/views/komunikacja.py` | `test_matchmaking.py::test_thread_reply_by_hub_notifies_author`, `test_wiedza.py::test_question_on_innovation_notifies_experts` |
| W-14 | Obserwowanie obszaru | Obserwujący dostaje powiadomienie o nowej innowacji i otwarciu naboru w obszarze | `app/views/komunikacja.py` `toggle_follow`, `app/views/admin.py` | `test_admin.py::test_toggle_call_notifies_followers` |
| W-15 | Ekspert ma listę pytań do siebie | `/ekspert` pokazuje wątki z obszarów eksperta; czekające (ostatnie słowo nie od Hubu ani eksperta) na górze; inne role dostają 403 | `app/views/komunikacja.py` `expert_inbox` | `test_matchmaking.py::test_expert_inbox_role_guard` |

## Funkcjonalne – Biblioteka, Tester, Kreator, Pośrednik (S)

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-16 | Biblioteka z filtrami | Filtry: obszar, powiat, etap, grupa odbiorców + wyszukiwanie; wartości spoza listy są ignorowane | `app/views/wiedza.py` `library` | `test_wiedza.py::test_library_filters` |
| W-17 | Tester innowacji | Zalogowany zgłasza test albo usprawnienie (≥ 10 znaków) lub ocenia 1–5; jedna ocena na osobę – nowa zastępuje poprzednią; każde działanie powiadamia Hub | `app/views/wiedza.py` `test_action` | `test_wiedza.py::test_one_rating_per_person_newest_wins`, `test_tester_actions_notify_hub` |
| W-18 | Fiszka pomysłu | Tytuł ≥ 3 znaki, istota ≥ 20 znaków, grupa i etap z listy; błędy przy polach, kod 422 | `app/views/kreator.py` `new` | `test_kreator.py::test_new_idea_validation_errors` |
| W-19 | Kanwa i wniosek edytuje tylko autor | Inny użytkownik dostaje 403; wydruk wniosku widzi autor i Hub | `app/views/kreator.py` `_own`, `print_application` | `test_kreator.py::test_only_owner_edits_canvas_and_applies`, `test_application_print_restricted` |
| W-20 | Asystent pomysłu działa zawsze | Z AI: mocne strony, pytania, kierunki, szkic prototypu (oznaczone jako AI); bez AI: wnioski z wypełnionych i pustych pól kanwy + podobne innowacje | `app/views/kreator.py` `ai_assistant`, `rule_assistant` | `test_kreator.py::test_full_creator_flow` |
| W-21 | Wniosek tylko w otwartym naborze | Generator działa tylko dla otwartego naboru przed terminem; złożenie wymaga wszystkich 7 pól; złożony wniosek jest tylko do odczytu | `app/views/kreator.py` `application` | `test_kreator.py::test_generator_inactive_for_closed_call`, `test_application_rejected_after_call_deadline` |
| W-22 | Karta usługi z Pośrednika | Karta ma 9 sekcji; koszty tylko jako rodzaje – każda kwota (także z odpowiedzi AI) zamieniona na „[kwota do wyceny]”; bez AI karta z szablonu i najlepiej dopasowanej innowacji; kartę widzi autor i Hub | `app/views/posrednik.py` | `test_posrednik_api.py::test_broker_rule_card_without_ai`, `test_broker_ai_card_is_labelled_and_strips_amounts`, `test_broker_card_private` |

## Funkcjonalne – panel Hubu (S)

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-23 | Panel tylko dla Hubu | Każda strona `/admin/*` wymaga roli admin: gość → wybór konta, inna rola → 403 (także dla POST) | `app/views/admin.py` `guard` | `test_admin.py::test_admin_pages_forbidden_for_other_roles`, `test_admin_post_forbidden_for_non_admin` |
| W-24 | Skrzynka spraw | Zgłoszenia nowe lub niezatwierdzone, pomysły i testy z 30 dni, złożone wnioski, prośby i zgłoszenia pilotażu; czekające na odpowiedź na górze | `app/views/admin.py` `inbox` | `test_admin.py::test_inbox_waiting_first_and_new_ideas_tile` |
| W-25 | Luki i trendy | Luka = najlepszy wynik < 0,35, same oceny „niepomocne” albo status „luka”; zgłoszenia zamknięte i połączone nie są luką; trendy: obszar w ostatnich 30 dniach vs poprzednich 30, mapa powiat × obszar | `app/views/admin.py` `gaps`, `trend_data` | `test_admin.py::test_gaps_list_and_trends`, `test_gaps_moved_to_trends_and_linked_reports_are_not_gaps` |
| W-26 | Edycja Biblioteki działa od razu | Zapis innowacji w panelu jest widoczny w dopasowaniach bez przebudowy indeksu | `app/views/admin.py` `edit_innovation`, `core/catalog.py` | `test_admin.py::test_quick_library_edit_is_live_in_matching` |
| W-27 | Import Biblioteki | CSV (`,`/`;`) albo JSON; każdy wiersz walidowany; raport z numerem wiersza; tytuł już istniejący (bez względu na wielkość liter i spacje) pomijany | `app/views/admin.py` `import_library` | `test_admin.py::test_import_csv_with_validation`, `test_import_twice_skips_duplicates` |
| W-28 | Eksport CSV bez ryzyka formuł | Zgłoszenia, luki i oceny jako CSV; komórka zaczynająca się od `=`, `+`, `-`, `@` dostaje apostrof | `app/views/admin.py` `export` | `test_admin.py::test_csv_export_and_formula_injection_guard` |
| W-29 | Nabory | Nowy nabór dodawany jako zamknięty; termin nie wcześniejszy niż dziś; otwarcie powiadamia obserwujących obszar | `app/views/admin.py` `new_call`, `toggle_call` | `test_admin.py::test_new_call_rejects_past_deadline` |
| W-30 | Moderacja po publikacji | Hub ukrywa i przywraca pomysł albo wiadomość; ukryte widzi tylko Hub; wpis w dzienniku | `app/views/admin.py` `toggle_hidden` | `test_admin.py::test_admin_hides_and_restores_idea_and_message` |
| W-31 | Zarządzanie kontami | Zmiana roli i blokada z wpisem w dzienniku; nie można zablokować siebie ani odebrać roli ostatniemu aktywnemu adminowi | `app/views/admin_users.py` | `test_admin_users.py::test_cannot_demote_last_admin_or_block_self` |

## Funkcjonalne – pilotaż „Razem z ZD” (C)

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| W-32 | Prośby rodzin | Prośbę wysyła tylko konto mieszkańca; pseudonim 2–40 znaków, powiat z listy, treść 10–1000; gość wybiera konto, a formularz czeka | `app/views/razem.py` `create_request`, `save_request` | `test_razem.py::test_request_validation`, `test_family_requests_only_from_resident_account`, `test_qa_fixes.py::test_guest_request_form_survives_login` |
| W-33 | Moderacja treści publicznych | Miejsca i sprzęt widać publicznie dopiero po zatwierdzeniu; pozostałe prośby Hub może tylko zamknąć | `app/views/admin.py` `razem_status` | `test_razem.py::test_public_lists_show_only_approved`, `test_guide_request_cannot_be_approved_only_closed` |
| W-34 | Jeden głos na Dzień Specjalistów | Drugi głos z tego samego konta nie jest zapisywany, użytkownik widzi „Twój głos już jest zapisany” | `app/views/razem.py` | `test_razem.py::test_specialists_day_one_vote_per_account` |
| W-35 | Pary w programie „Jestem potrzebny” | Propozycja pary tylko przy tym samym powiecie, wolnych miejscach, pasującym zainteresowaniu i grupie wiekowej; dwa kliknięcia „Połącz” tworzą jedną misję; oferta bez wolnych miejsc odrzuca połączenie | `app/views/admin_potrzebny.py` `pair_proposals`, `pair` | `test_potrzebny.py::test_pair_rules_powiat_interest_age_and_buddy`, `test_double_connect_creates_one_mission`, `test_pair_rejected_when_offer_has_no_free_slots` |
| W-36 | Dzienniczek z odznakami | Odznaki od sumy misji, odznaka tematyczna od 3 misji danego rodzaju, umiejętności od 5 misji | `data/potrzebny.py` `badges_for`, `skills_for` | `test_potrzebny.py::test_badges_and_skills_thresholds` |
| W-37 | Wizyty dziecka nie trafiają na serwer | Lista wizyt istnieje tylko w `localStorage` przeglądarki | `app/static/js/razem.js` | `test_razem.py::test_visits_page_is_browser_only` |
| W-38 | Mapa miejsc pracy ze źródłem | Propozycja miejsca wymaga linku `http(s)` do źródła; na mapie dopiero po zatwierdzeniu przez Hub | `app/views/praca.py` `propose` | `test_potrzebny.py::test_workplace_proposal_needs_source_and_approval` |

## Niefunkcjonalne

| ID | Wymaganie | Kryterium akceptacji | Gdzie zrealizowane | Test |
|---|---|---|---|---|
| N-01 | AI opcjonalne i bezpieczne | Bez klucza, po przekroczeniu dziennego limitu, po timeoucie 25 s albo przy odpowiedzi spoza schematu aplikacja działa na regułach i szablonach; nigdy błąd 500; treść od AI zawsze oznaczona | `core/ai.py` | `test_ai_bezpieczenstwo.py::test_ai_never_raises_and_returns_none`, `test_invalid_ai_reply_is_rejected_and_rules_still_work`, `test_daily_limit_falls_back_and_cache_does_not_spend` |
| N-02 | Odporność na prompt injection | Tekst użytkownika trafia do modelu tylko w ogranicznikach `<dane_zewnetrzne>`, przycięty do 8000 znaków; polecenie w opisie nie zmienia obszaru, statusu ani dopasowania | `core/ai.py`, `core/catalog.py` | `test_ai_bezpieczenstwo.py::test_injected_description_does_not_change_decisions` |
| N-03 | Dostępność WCAG 2.1 AA | 0 naruszeń wykrywanych automatycznie (axe-core) na wszystkich widokach, na desktopie i 320 px; audyt w CI blokuje scalenie | `scripts/axe_audit.py`, `.github/workflows/ci.yml` | raport [WCAG_RAPORT.md](WCAG_RAPORT.md) |
| N-04 | Działanie bez JavaScriptu | Wszystkie ścieżki działają bez JS, w tym A+ i wysoki kontrast (ciasteczko); wyjątek: lista wizyt (W-37) | szablony, `app/auth.py` `toggle_pref` | `test_app.py::test_a11y_prefs_toggle_cookie` |
| N-05 | Bezpieczeństwo formularzy i sesji | POST bez tokenu CSRF → 400; nagłówki CSP bez skryptów i stylów inline; ciasteczko sesji HttpOnly i SameSite; przekierowania tylko w obrębie serwisu | `app/__init__.py`, `app/auth.py` `safe_next` | `test_app.py::test_post_without_csrf_rejected`, `test_security_headers`, `test_open_redirect_blocked` |
| N-06 | Role sprawdzane na serwerze | Każdy widok z ograniczeniem roli zwraca 403 dla innej roli niezależnie od tego, co pokazuje interfejs | `app/auth.py` `role_required` | `test_admin.py`, `test_potrzebny.py::test_only_matching_role_can_submit` |
| N-07 | Język i komunikaty po polsku | Strony błędów 400–500 po polsku, w układzie aplikacji; odmiana liczebników | `app/__init__.py` `ERRORS`, `plural` | `test_app.py::test_friendly_500_in_app_layout`, `test_admin.py::test_plural_filter` |
| N-08 | Konfiguracja jawna | Każda zmienna środowiskowa czytana w kodzie jest opisana w README | README, sekcja „Konfiguracja” | `test_readme_config.py` |
| N-09 | Jedno polecenie do wdrożenia | Obraz Docker z healthcheckiem `/zdrowie`, baza w wolumenie | `Dockerfile`, `docker-compose.yml` | `test_app.py::test_health_endpoint` |
