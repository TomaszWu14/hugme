import re

import pytest

from app import create_app


@pytest.fixture(autouse=True)
def no_ai(monkeypatch):
    monkeypatch.setenv("AI_DISABLED", "1")


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"), "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_of(client, path="/"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


def login(client, role):
    """Loguje na konto demo danej roli; zwraca token CSRF sesji."""
    ids = {"mieszkaniec": 1, "ngo": 2, "gmina": 3, "ekspert": 4, "admin": 5}
    token = csrf_of(client, "/konto")
    client.post("/konto", data={"_csrf": token, "user_id": ids[role]})
    return csrf_of(client, "/")
