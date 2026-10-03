from core import db


def test_seed_volumes_and_fictional_marking(app):
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM innovations")[0] == 24
        assert db.one("SELECT COUNT(*) FROM reports")[0] == 22
        assert db.one("SELECT COUNT(*) FROM users WHERE is_demo = 1")[0] == 5
        assert db.one("SELECT COUNT(*) FROM ideas")[0] == 2
        assert db.one("SELECT COUNT(DISTINCT powiat) FROM reports")[0] >= 12
        # Zgłoszenia z ostatnich 120 dni
        assert db.one("SELECT COUNT(*) FROM reports WHERE created_at < datetime('now', '-121 days')")[0] == 0
        # Każda organizacja w bibliotece jest oznaczona jako przykład
        assert db.one("SELECT COUNT(*) FROM innovations WHERE org NOT LIKE '%(PRZYKŁAD)%'")[0] == 0
        # Dopasowania policzone dla zgłoszeń
        assert db.one("SELECT COUNT(*) FROM reports WHERE best_score > 0")[0] >= 20


def test_reports_describe_groups_not_people(app):
    from core.privacy import mask
    with app.app_context():
        for r in db.query("SELECT body FROM reports"):
            assert mask(r["body"])[1] == [], r["body"]
