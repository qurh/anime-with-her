import json
from pathlib import Path


def test_root_scripts_are_declared():
    data = json.loads(Path("package.json").read_text(encoding="utf-8"))
    assert data["scripts"]["dev:backend"] == "uvicorn app.main:app --reload --app-dir apps/backend"
    assert data["scripts"]["dev:worker"] == "powershell -ExecutionPolicy Bypass -File ./scripts/dev-worker.ps1"
    assert data["scripts"]["dev:web"] == "powershell -ExecutionPolicy Bypass -File ./scripts/dev-web.ps1"
    assert data["scripts"]["test:backend"] == "python -m pytest -q apps/backend/tests"
