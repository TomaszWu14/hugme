"""Powiadomienie push (ntfy) o nowym odwiedzającym demo: tylko po udanym zapisie, w tle, nigdy nie psuje wejścia."""
import pytest

from app import create_app, visitor_notify
from tests.test_gate import submit, visitors

URL = "https://ntfy.example/tajny-temat"


@pytest.fixture
def gated(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "n.db"), "SECRET_KEY": "t", "DEMO_MODE": True,
                       "DEMO_VISITOR_GATE": True})


@pytest.fixture
def gc(gated):
    return gated.test_client()


class SyncThread:
    """Zamiast wątku w tle – wykonanie od razu, żeby test widział wysyłkę."""

    def __init__(self, target, args=(), daemon=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


@pytest.fixture
def sent(monkeypatch):
    calls = []

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b""

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        return Resp()

    monkeypatch.setattr(visitor_notify.threading, "Thread", SyncThread)
    monkeypatch.setattr(visitor_notify.urllib.request, "urlopen", fake_urlopen)
    return calls


def test_valid_form_sends_one_notification(monkeypatch, gc, sent):
    monkeypatch.setenv("NTFY_URL", URL)
    assert submit(gc).status_code == 302
    assert len(sent) == 1
    req, timeout = sent[0]
    assert req.full_url == URL and req.get_method() == "POST" and timeout == 5
    assert req.data.decode("utf-8") == "Anna Kowalska (Acme Sp. z o.o.) wszedł do hugme"
    headers = {k.lower(): v for k, v in req.header_items()}
    assert headers["title"] == "Nowy gosc: hugme" and headers["tags"] == "bell" and headers["priority"] == "high"
    assert "authorization" not in headers
    assert all(v.isascii() for v in headers.values())


def test_token_adds_authorization_header(monkeypatch, gc, sent):
    monkeypatch.setenv("NTFY_URL", URL)
    monkeypatch.setenv("NTFY_TOKEN", "tk_sekret")
    submit(gc)
    assert dict(sent[0][0].header_items())["Authorization"] == "Bearer tk_sekret"


@pytest.mark.parametrize("over", [{"website": "http://spam"}, {"first_name": None}, {"consent": None},
                                  {"company": "jan@x.pl"}])
def test_honeypot_or_bad_data_sends_nothing(monkeypatch, gc, sent, over):
    monkeypatch.setenv("NTFY_URL", URL)
    assert submit(gc, **over).status_code in (400, 422)
    assert sent == []


def test_no_url_sends_nothing(gated, gc, sent):
    assert submit(gc).status_code == 302
    assert sent == [] and len(visitors(gated)) == 1


def test_send_error_does_not_break_entry(monkeypatch, gated, gc, sent):
    monkeypatch.setenv("NTFY_URL", URL)

    def boom(req, timeout):
        raise OSError("sieć leży")

    monkeypatch.setattr(visitor_notify.urllib.request, "urlopen", boom)
    r = submit(gc)
    assert r.status_code == 302 and r.headers["Location"] == "/biblioteka"
    assert len(visitors(gated)) == 1 and gc.get("/biblioteka").status_code == 200


def test_body_is_truncated_to_300_chars(monkeypatch, sent):
    monkeypatch.setenv("NTFY_URL", URL)
    visitor_notify.notify_visitor("A" * 100, "B" * 100, "C" * 100)
    assert len(sent[0][0].data.decode("utf-8")) == 300


def test_runs_in_daemon_thread(monkeypatch):
    monkeypatch.setenv("NTFY_URL", URL)
    started = []

    class Spy(SyncThread):
        def __init__(self, target, args=(), daemon=None):
            started.append(daemon)

        def start(self):
            pass

    monkeypatch.setattr(visitor_notify.threading, "Thread", Spy)
    visitor_notify.notify_visitor("Anna", "Kowalska", "Acme")
    assert started == [True]


def test_non_http_url_is_ignored(monkeypatch):
    from app import visitor_notify

    started = []
    monkeypatch.setenv("NTFY_URL", "file:///etc/passwd")
    monkeypatch.setattr(visitor_notify.threading, "Thread", lambda *a, **k: started.append(k) or None)
    visitor_notify.notify_visitor("Jan", "Kowalski", "ACME")
    assert started == []
