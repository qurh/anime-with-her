import json
from pathlib import Path


def test_root_scripts_are_declared():
    data = json.loads(Path("package.json").read_text(encoding="utf-8"))
    assert "dev:backend" in data["scripts"]
