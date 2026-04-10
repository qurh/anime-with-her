from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from urllib.parse import unquote


DEFAULT_UPLOAD_DIR = Path("data/input")
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _resolve_upload_dir() -> Path:
    value = os.getenv("ANIME_WITH_HER_UPLOAD_DIR")
    if value:
        return Path(value)
    return DEFAULT_UPLOAD_DIR


def _normalize_filename(filename: str | None) -> str:
    raw_name = unquote(filename or "").strip()
    basename = Path(raw_name).name if raw_name else "uploaded-video.mp4"
    sanitized = _SAFE_NAME_RE.sub("_", basename).strip("._")
    if not sanitized:
        sanitized = "uploaded-video.mp4"
    if "." not in sanitized:
        sanitized = f"{sanitized}.mp4"
    return sanitized


def _to_display_path(path: Path) -> str:
    repo_root = Path.cwd().resolve()
    resolved = path.resolve()
    if resolved.is_relative_to(repo_root):
        return resolved.relative_to(repo_root).as_posix()
    return resolved.as_posix()


def save_uploaded_video(content: bytes, filename: str | None, content_type: str) -> dict[str, object]:
    if not content:
        raise ValueError("Uploaded file is empty.")

    upload_dir = _resolve_upload_dir()
    upload_dir.mkdir(parents=True, exist_ok=True)

    final_name = _normalize_filename(filename)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    target = upload_dir / f"{timestamp}_{uuid4().hex[:8]}_{final_name}"
    target.write_bytes(content)

    return {
        "stored_path": _to_display_path(target),
        "original_filename": final_name,
        "size_bytes": len(content),
        "content_type": content_type,
    }
