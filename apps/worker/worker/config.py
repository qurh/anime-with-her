import os
from dataclasses import dataclass, field
from typing import Literal

WorkerMode = Literal["fake", "hybrid", "real"]
_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class WorkerConfig:
    mode: WorkerMode
    real_stages: set[str] = field(default_factory=set)

    def should_use_real(self, stage_name: str) -> bool:
        if self.mode == "real":
            return True
        if self.mode == "fake":
            return False
        return stage_name in self.real_stages


def load_worker_config() -> WorkerConfig:
    raw_mode = os.getenv("WORKER_MODE", "fake").strip().lower()
    mode: WorkerMode
    if raw_mode in {"fake", "hybrid", "real"}:
        mode = raw_mode
    else:
        mode = "fake"

    raw_real_stages = os.getenv("WORKER_REAL_STAGES", "")
    real_stages = {item.strip() for item in raw_real_stages.split(",") if item.strip()}
    return WorkerConfig(mode=mode, real_stages=real_stages)


def asr_runtime_env_ready() -> bool:
    if os.getenv("ASR_RUNTIME_READY", "").strip().lower() in _TRUE_VALUES:
        return True
    return any(
        os.getenv(env_name, "").strip()
        for env_name in ("ASR_MODEL_PATH", "WHISPER_MODEL", "WHISPER_MODEL_PATH")
    )
