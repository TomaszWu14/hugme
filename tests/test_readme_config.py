"""Issue #28: każda zmienna środowiskowa czytana w kodzie ma wiersz w tabeli „Konfiguracja” w README."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_READ = re.compile(r'os\.environ(?:\.get\(|\[)\s*"([A-Z_]+)"')


def test_every_env_var_is_documented():
    used = {name for d in ("app", "core", "data", "scripts") for f in (ROOT / d).rglob("*.py")
            for name in ENV_READ.findall(f.read_text(encoding="utf-8"))}
    section = ROOT.joinpath("README.md").read_text(encoding="utf-8").split("## Konfiguracja", 1)[1].split("\n## ", 1)[0]
    documented = set(re.findall(r"^\| `([A-Z_]+)`", section, re.M))
    assert used and used <= documented, sorted(used - documented)
