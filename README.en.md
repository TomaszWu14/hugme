# HugMe – matching residents' problems with existing social innovations

🇵🇱 [Wersja polska (pełna)](README.md) · 🇬🇧 English summary

**A resident, a municipality or an NGO describes a problem in plain words and gets proven solutions from the region,
while the regional Social Innovation Hub sees where solutions are missing.** A prototype for the Małopolska Social
Innovation Hub (ROPS Kraków), built solo at HackYeah 2026.

[![Tests](https://github.com/TomaszWu14/hugme/actions/workflows/ci.yml/badge.svg)](https://github.com/TomaszWu14/hugme/actions/workflows/ci.yml)

🏆 **HackYeah 2026 jury score: 7.30 vs. 5.65 average across all teams** – highest for how well it met the challenge
(7.67). [All criteria](README.md#ocena-jury).

![demo](docs/screenshots/demo.gif)

📹 **[1:46 walkthrough with voice-over (YouTube, Polish)](https://youtu.be/MpFg-FN4G50)** ·
🌐 **Live demo:** [hugme.twapp.pl](https://hugme.twapp.pl) – password-less demo accounts, pick a role in the top bar;
data resets after 20 minutes of inactivity. The demo may be switched off without notice – it runs locally in about
2 minutes (below). The UI is in Polish.

## Problem → solution

Many social innovations already work in the region, but the people who need them don't know about them, the next
municipality builds from scratch what already exists, and the Hub can't see where help is missing. HugMe takes a
plain-language description, **masks personal data** (PESEL, phone, e-mail, address, a child's name) before anything
is stored, and matches it against the Innovation Library with **explainable rules** ("matches because: shared words
and topics"). A saved request becomes a thread with the Hub, the author rates relevance, and requests without a good
solution become **gaps** – input for the topics of the next funding calls.

## What's inside

- **7 of 7 modules from the brief:** matchmaking, knowledge base, idea builder with grant-application generator,
  innovation tester, messaging, Hub admin panel (users and roles), and an innovation broker for municipalities/NGOs.
- **Explainable matching without AI:** BM25 + custom Polish stemming + a concept dictionary; 16/16 test sentences
  land in the top 3. When nothing fits, the app says so and the case goes to the Hub as a gap.
- **Optional AI (Claude Haiku)** only widens the query and drafts helper text – it never decides. Input is fenced as
  data, output is validated JSON; no key = rules and templates, with a daily cost cap.
- **Accessibility (WCAG 2.1 AA):** server-rendered pages work without JavaScript; axe-core audit in CI at 320 px and
  desktop, larger text and high-contrast modes, 44 px touch targets.
- **378 tests** (paths, roles, CSRF, privacy masking, matching relevance, AI safety) and security scans on every PR
  (gitleaks, Bandit, Semgrep, Trivy, pip-audit).

## Run locally

Python 3.12+.

```bash
git clone https://github.com/TomaszWu14/hugme.git && cd hugme
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
DEMO_ACCOUNTS=1 flask --app app:create_app run      # http://127.0.0.1:5000, guided scenarios at /demo
pytest
```

The SQLite database `instance/hugme.db` is created with sample data on first start. Docker:
`SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") docker compose up -d --build`.
All configuration is via environment variables – see the table in the [Polish README](README.md#konfiguracja).

## Stack and why

| Part | Why |
|---|---|
| Python 3.12, Flask, Jinja | server-rendered, works without JS on old phones and with screen readers; 3 production dependencies |
| BM25 + stemming + concept dictionary | explainable, deterministic, testable matching with no API cost |
| SQLite, PostgreSQL-compatible schema | one file in a volume is enough for a prototype; migration path documented |
| Docker + Coolify | one container with a healthcheck, deployed on merge to `main` |
| pytest + axe-core (Playwright) in CI | a change that breaks a user path or WCAG can't be merged |

## Documentation (Polish)

Business-analysis docs: [problem & scope](docs/01-problem-i-zakres.md) · [process (Mermaid)](docs/02-proces.md) ·
[user flow, 63 screens](docs/03-user-flow.md) · [data model, 22-table ERD](docs/04-model-danych.md) ·
[47 requirements with acceptance criteria](docs/05-wymagania.md) · [11 decision records](docs/06-decyzje.md) ·
[limitations & 16 known issues](docs/07-ograniczenia.md) · [architecture](docs/ARCHITEKTURA.md) ·
[data & GDPR](docs/DANE.md) · [accessibility](docs/WCAG.md).

## Scope and limitations

A hackathon prototype, not a production system: no real login (password-less demo accounts), no outgoing e-mail
(queued in the panel), no self-service data deletion. Sample data is fictional (marked "PRZYKŁAD"), except job
listings and statistics in the "Praca" tab, which cite public sources.

## Context and licence

Built solo during HackYeah 2026 (HubMi.pl challenge) and refined afterwards. I analysed the brief, made product
decisions up front ([100 Q&A](docs/archiwum/BRAINSTORM.md)), turned business rules into acceptance tests and verified
the result; code was written with Claude Code as a programming assistant (commits carry `Co-Authored-By: Claude`).
Code under the [MIT licence](LICENSE).
