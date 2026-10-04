"""Lokalny serwer HugMe na świeżej bazie z danymi przykładowymi – dla zrzutów i nagrań.

Kod aplikacji bierzemy z katalogu repo albo z HUGME_ROOT (np. czysta kopia main)."""
import os
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(os.environ.get("HUGME_ROOT") or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("AI_DISABLED", "1")  # nagrania bez AI: powtarzalne i bez kosztów


def start(port):
    from werkzeug.serving import make_server
    from app import create_app
    app = create_app({"DATABASE": str(Path(tempfile.mkdtemp()) / "demo.db"), "SECRET_KEY": "demo"})
    srv = make_server("127.0.0.1", port, app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{port}"
