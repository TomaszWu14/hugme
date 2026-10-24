"""SECRET_KEY: bez zmiennej klucz jest trwały (plik obok bazy), jawna konfiguracja ma pierwszeństwo."""
import stat

from app import create_app


def _app(tmp_path, **extra):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "d" / "h.db"), **extra})


def test_klucz_stabilny_miedzy_startami(tmp_path, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    a, b = _app(tmp_path), _app(tmp_path)
    assert a.config["SECRET_KEY"] == b.config["SECRET_KEY"]
    assert len(a.config["SECRET_KEY"]) >= 32
    f = tmp_path / "d" / ".secret_key"
    assert stat.S_IMODE(f.stat().st_mode) == 0o600
    assert not list(f.parent.glob("*.tmp"))


def test_jawny_klucz_ma_pierwszenstwo(tmp_path, monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    app = _app(tmp_path, SECRET_KEY="jawny")
    assert app.config["SECRET_KEY"] == "jawny"
    assert not (tmp_path / "d" / ".secret_key").exists()


def test_env_ma_pierwszenstwo(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "z-env")
    assert _app(tmp_path).config["SECRET_KEY"] == "z-env"
