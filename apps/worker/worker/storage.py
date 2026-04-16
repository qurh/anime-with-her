from pathlib import Path


def _to_posix(path: Path) -> str:
    return path.as_posix()


def build_episode_layout(episode_id: str, root: str = "data/episodes") -> dict[str, str]:
    base = Path(root) / episode_id
    return {
        "input": _to_posix(base / "input"),
        "analysis": _to_posix(base / "analysis"),
        "generation": _to_posix(base / "generation"),
        "review": _to_posix(base / "review"),
        "output": _to_posix(base / "output"),
        "logs": _to_posix(base / "logs"),
    }
