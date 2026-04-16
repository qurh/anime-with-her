# AI Dubbing Director Console Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a from-scratch MVP for an AI dubbing director console that produces one episode at a time, stores character assets at the season level, pauses for character confirmation before full-episode generation, and supports key-segment refinement.

**Architecture:** Use a monorepo with a FastAPI backend for orchestration and metadata, a Python worker for deterministic pipeline stages, and a Next.js web console for the director workflow. Keep real AI/media models behind adapters so the first MVP can be tested with deterministic fakes.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic, pytest, local JSON-friendly repositories, Next.js, React, TypeScript, local filesystem storage, future adapters for FFmpeg, ASR, diarization, LLM, TTS, and mixing.

## Execution Rules

- Use @superpowers:test-driven-development for every implementation task.
- Use @superpowers:verification-before-completion before claiming a task complete.
- Keep changes DRY and YAGNI. Do not integrate real models until deterministic contracts pass.
- Commit after each task.
- Treat `docs/design/2026-04-16-ai-dubbing-director-console-integrated-design-v2-1.md` as the source of truth.

## Phase 1: Repository Skeleton and Shared Contracts

### Task 1: Monorepo Skeleton and Root Commands

**Files:**
- Create: `package.json`
- Modify: `README.md`
- Create: `apps/backend/pyproject.toml`
- Create: `apps/worker/pyproject.toml`
- Create: `apps/web/package.json`
- Create: `scripts/dev-backend.ps1`
- Create: `scripts/dev-worker.ps1`
- Create: `scripts/dev-web.ps1`
- Create: `tests/unit/test_root_scripts.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_root_scripts.py
import json
from pathlib import Path


def test_root_scripts_are_declared():
    data = json.loads(Path("package.json").read_text(encoding="utf-8"))
    assert data["scripts"]["dev:backend"] == "uvicorn app.main:app --reload --app-dir apps/backend"
    assert data["scripts"]["dev:worker"] == "powershell -ExecutionPolicy Bypass -File ./scripts/dev-worker.ps1"
    assert data["scripts"]["dev:web"] == "powershell -ExecutionPolicy Bypass -File ./scripts/dev-web.ps1"
    assert data["scripts"]["test:backend"] == "python -m pytest -q apps/backend/tests"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_root_scripts.py -v`  
Expected: FAIL because `package.json` does not exist.

**Step 3: Write minimal implementation**

Create `package.json`:

```json
{
  "name": "anime-with-her",
  "private": true,
  "scripts": {
    "dev:backend": "uvicorn app.main:app --reload --app-dir apps/backend",
    "dev:worker": "powershell -ExecutionPolicy Bypass -File ./scripts/dev-worker.ps1",
    "dev:web": "powershell -ExecutionPolicy Bypass -File ./scripts/dev-web.ps1",
    "test:backend": "python -m pytest -q apps/backend/tests"
  }
}
```

Create backend and worker `pyproject.toml` files with `requires-python = ">=3.12"` and dependencies on `fastapi`, `uvicorn`, `pydantic`, and `pytest` where needed. Create `apps/web/package.json` with `next`, `react`, `react-dom`, `typescript`, and smoke scripts. Create the three PowerShell dev scripts to run backend, worker, and web.

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_root_scripts.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add package.json README.md apps scripts tests/unit/test_root_scripts.py
git commit -m "chore(repo): scaffold director console monorepo"
```

### Task 2: Core Domain Models

**Files:**
- Create: `apps/backend/app/__init__.py`
- Create: `apps/backend/app/domain/__init__.py`
- Create: `apps/backend/app/domain/models.py`
- Create: `apps/backend/tests/unit/test_domain_models.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/unit/test_domain_models.py
from app.domain.models import Episode, EpisodeState, SeasonCharacterProfile, StageState


def test_episode_defaults_to_draft_state():
    episode = Episode(episode_id="ep_001", series_id="series_001", season_id="season_001", title="第 1 集")
    assert episode.state == EpisodeState.DRAFT


def test_character_profile_requires_style_card():
    profile = SeasonCharacterProfile(
        profile_id="profile_001",
        series_character_id="char_001",
        season_id="season_001",
        display_name="女主角",
        style_card_id="card_001",
    )
    assert profile.style_card_id == "card_001"


def test_stage_state_supports_review_gate():
    assert StageState.NEEDS_REVIEW.value == "needs_review"
    assert StageState.APPROVED.value == "approved"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_domain_models.py -v`  
Expected: FAIL because `app.domain.models` does not exist.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/domain/models.py
from enum import Enum
from pydantic import BaseModel, Field


class EpisodeState(str, Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    NEEDS_CHARACTER_REVIEW = "needs_character_review"
    CHARACTER_APPROVED = "character_approved"
    GENERATING = "generating"
    NEEDS_SEGMENT_REVIEW = "needs_segment_review"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHED = "published"
    FAILED = "failed"


class StageState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Episode(BaseModel):
    episode_id: str
    series_id: str
    season_id: str
    title: str
    state: EpisodeState = EpisodeState.DRAFT


class SeasonCharacterProfile(BaseModel):
    profile_id: str
    series_character_id: str
    season_id: str
    display_name: str
    style_card_id: str


class CharacterStyleCard(BaseModel):
    style_card_id: str
    profile_id: str
    base_tone: str
    speech_rate: str
    emotion_range: list[str] = Field(default_factory=list)
    forbidden_styles: list[str] = Field(default_factory=list)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_domain_models.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app apps/backend/tests/unit/test_domain_models.py
git commit -m "feat(domain): add director console core schemas"
```

### Task 3: FastAPI Bootstrap and Health API

**Files:**
- Create: `apps/backend/app/main.py`
- Create: `apps/backend/app/api/routes/health.py`
- Create: `apps/backend/tests/conftest.py`
- Create: `apps/backend/tests/api/test_health_api.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/api/test_health_api.py
def test_health_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"success": True, "data": {"status": "ok"}}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_health_api.py -v`  
Expected: FAIL because FastAPI app is missing.

**Step 3: Write minimal implementation**

```python
# apps/backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
```

```python
# apps/backend/app/main.py
from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI(title="anime-with-her director console")
app.include_router(health_router, prefix="/api/v1")
```

```python
# apps/backend/app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"success": True, "data": {"status": "ok"}}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_health_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app apps/backend/tests
git commit -m "feat(api): bootstrap director console backend"
```

## Phase 2: Asset Model and Episode Lifecycle

### Task 4: In-Memory Asset Repository

**Files:**
- Create: `apps/backend/app/repositories/__init__.py`
- Create: `apps/backend/app/repositories/memory_store.py`
- Create: `apps/backend/tests/unit/test_memory_store.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/unit/test_memory_store.py
from app.repositories.memory_store import MemoryStore


def test_store_creates_series_season_episode():
    store = MemoryStore()
    series = store.create_series(title="示例动漫")
    season = store.create_season(series.series_id, title="第一季")
    episode = store.create_episode(series.series_id, season.season_id, title="第 1 集")

    assert series.series_id.startswith("series_")
    assert season.series_id == series.series_id
    assert episode.season_id == season.season_id
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_memory_store.py -v`  
Expected: FAIL because repository does not exist.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/repositories/memory_store.py
from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesRecord:
    series_id: str
    title: str


@dataclass(frozen=True)
class SeasonRecord:
    season_id: str
    series_id: str
    title: str


@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    series_id: str
    season_id: str
    title: str


class MemoryStore:
    def __init__(self):
        self._next_series = 1
        self._next_season = 1
        self._next_episode = 1
        self.series = {}
        self.seasons = {}
        self.episodes = {}

    def create_series(self, title: str) -> SeriesRecord:
        record = SeriesRecord(series_id=f"series_{self._next_series}", title=title)
        self._next_series += 1
        self.series[record.series_id] = record
        return record

    def create_season(self, series_id: str, title: str) -> SeasonRecord:
        record = SeasonRecord(season_id=f"season_{self._next_season}", series_id=series_id, title=title)
        self._next_season += 1
        self.seasons[record.season_id] = record
        return record

    def create_episode(self, series_id: str, season_id: str, title: str) -> EpisodeRecord:
        record = EpisodeRecord(
            episode_id=f"episode_{self._next_episode}",
            series_id=series_id,
            season_id=season_id,
            title=title,
        )
        self._next_episode += 1
        self.episodes[record.episode_id] = record
        return record
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_memory_store.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/repositories apps/backend/tests/unit/test_memory_store.py
git commit -m "feat(repo): add in-memory asset repository"
```

### Task 5: Series, Season, Episode APIs

**Files:**
- Create: `apps/backend/app/api/routes/assets.py`
- Modify: `apps/backend/app/main.py`
- Create: `apps/backend/tests/api/test_assets_api.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/api/test_assets_api.py
def test_create_series_season_episode(client):
    series = client.post("/api/v1/series", json={"title": "示例动漫"})
    assert series.status_code == 201
    series_id = series.json()["data"]["series_id"]

    season = client.post(f"/api/v1/series/{series_id}/seasons", json={"title": "第一季"})
    assert season.status_code == 201
    season_id = season.json()["data"]["season_id"]

    episode = client.post(
        f"/api/v1/series/{series_id}/seasons/{season_id}/episodes",
        json={"title": "第 1 集"},
    )
    assert episode.status_code == 201
    assert episode.json()["data"]["episode_id"].startswith("episode_")
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_assets_api.py -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/api/routes/assets.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.repositories.memory_store import MemoryStore

router = APIRouter()
store = MemoryStore()


class CreateAssetRequest(BaseModel):
    title: str


@router.post("/series", status_code=201)
def create_series(payload: CreateAssetRequest):
    return {"success": True, "data": store.create_series(payload.title).__dict__}


@router.post("/series/{series_id}/seasons", status_code=201)
def create_season(series_id: str, payload: CreateAssetRequest):
    return {"success": True, "data": store.create_season(series_id, payload.title).__dict__}


@router.post("/series/{series_id}/seasons/{season_id}/episodes", status_code=201)
def create_episode(series_id: str, season_id: str, payload: CreateAssetRequest):
    return {"success": True, "data": store.create_episode(series_id, season_id, payload.title).__dict__}
```

Wire in `apps/backend/app/main.py`:

```python
from app.api.routes.assets import router as assets_router
app.include_router(assets_router, prefix="/api/v1")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_assets_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api apps/backend/app/main.py apps/backend/tests/api/test_assets_api.py
git commit -m "feat(api): add series season episode endpoints"
```

## Phase 3: Worker Pipeline Contracts

### Task 6: Worker Stage Manifest and Episode Layout

**Files:**
- Create: `apps/worker/worker/__init__.py`
- Create: `apps/worker/worker/main.py`
- Create: `apps/worker/worker/manifest.py`
- Create: `apps/worker/worker/storage.py`
- Create: `tests/unit/test_worker_contracts.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_worker_contracts.py
from worker.manifest import build_stage_manifest
from worker.storage import build_episode_layout


def test_manifest_records_review_state():
    manifest = build_stage_manifest(
        episode_id="episode_1",
        stage_name="character_analysis",
        state="needs_review",
        input_refs=["source.mp4"],
        output_refs=["character_candidates.json"],
    )
    assert manifest["state"] == "needs_review"
    assert manifest["stage_name"] == "character_analysis"


def test_episode_layout_contains_required_directories():
    layout = build_episode_layout("episode_1")
    assert layout["analysis"].endswith("data/episodes/episode_1/analysis")
    assert layout["generation"].endswith("data/episodes/episode_1/generation")
    assert layout["review"].endswith("data/episodes/episode_1/review")
```

**Step 2: Run test to verify it fails**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_worker_contracts.py -v`  
Expected: FAIL because worker modules do not exist.

**Step 3: Write minimal implementation**

```python
# apps/worker/worker/manifest.py
from datetime import UTC, datetime


def build_stage_manifest(episode_id: str, stage_name: str, state: str, input_refs: list[str], output_refs: list[str]):
    return {
        "episode_id": episode_id,
        "stage_name": stage_name,
        "state": state,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "created_at": datetime.now(UTC).isoformat(),
    }
```

```python
# apps/worker/worker/storage.py
from pathlib import Path


def build_episode_layout(episode_id: str, root: str = "data/episodes") -> dict[str, str]:
    base = Path(root) / episode_id
    return {
        "input": str(base / "input"),
        "analysis": str(base / "analysis"),
        "generation": str(base / "generation"),
        "review": str(base / "review"),
        "output": str(base / "output"),
        "logs": str(base / "logs"),
    }
```

```python
# apps/worker/worker/main.py
def main():
    print("anime-with-her worker ready")


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_worker_contracts.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker tests/unit/test_worker_contracts.py
git commit -m "feat(worker): add pipeline manifest and storage contracts"
```

### Task 7: Fake Character Analysis Pipeline

**Files:**
- Create: `apps/worker/worker/pipelines/__init__.py`
- Create: `apps/worker/worker/pipelines/character_analysis.py`
- Create: `tests/unit/test_character_analysis_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_character_analysis_pipeline.py
from worker.pipelines.character_analysis import run_character_analysis


def test_character_analysis_returns_review_payload():
    result = run_character_analysis(episode_id="episode_1", source_video="demo.mp4")
    assert result["stage_name"] == "character_analysis"
    assert result["state"] == "needs_review"
    assert result["review_payload"]["characters"][0]["display_name"] == "角色候选 1"
    assert result["review_payload"]["style_cards"][0]["base_tone"]
```

**Step 2: Run test to verify it fails**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_character_analysis_pipeline.py -v`  
Expected: FAIL because pipeline does not exist.

**Step 3: Write minimal implementation**

```python
# apps/worker/worker/pipelines/character_analysis.py
from worker.manifest import build_stage_manifest


def run_character_analysis(episode_id: str, source_video: str) -> dict[str, object]:
    review_payload = {
        "characters": [{"candidate_id": "candidate_1", "display_name": "角色候选 1", "confidence": 0.82}],
        "style_cards": [{"candidate_id": "candidate_1", "base_tone": "冷静但情绪压抑", "speech_rate": "中速"}],
    }
    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="character_analysis",
        state="needs_review",
        input_refs=[source_video],
        output_refs=[f"data/episodes/{episode_id}/analysis/character_candidates.json"],
    )
    return {**manifest, "review_payload": review_payload}
```

**Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_character_analysis_pipeline.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/pipelines tests/unit/test_character_analysis_pipeline.py
git commit -m "feat(worker): add fake character analysis pipeline"
```

## Phase 4: Review Gate and Generation APIs

### Task 8: Character Analysis and Approval APIs

**Files:**
- Create: `apps/backend/app/api/routes/analysis.py`
- Modify: `apps/backend/app/main.py`
- Create: `apps/backend/tests/api/test_character_analysis_api.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/api/test_character_analysis_api.py
def test_start_character_analysis_moves_episode_to_review(client):
    response = client.post(
        "/api/v1/episodes/episode_1/analysis/character",
        json={"source_video": "data/episodes/episode_1/input/source.mp4"},
    )
    assert response.status_code == 202
    assert response.json()["data"]["state"] == "needs_review"


def test_approve_character_analysis_returns_approved_state(client):
    response = client.post(
        "/api/v1/episodes/episode_1/analysis/character/approve",
        json={"approved_characters": [{"candidate_id": "candidate_1", "display_name": "女主角", "base_tone": "温柔但坚定"}]},
    )
    assert response.status_code == 200
    assert response.json()["data"]["state"] == "approved"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_character_analysis_api.py -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/api/routes/analysis.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class StartCharacterAnalysisRequest(BaseModel):
    source_video: str


class ApprovedCharacter(BaseModel):
    candidate_id: str
    display_name: str
    base_tone: str


class ApproveCharacterAnalysisRequest(BaseModel):
    approved_characters: list[ApprovedCharacter]


@router.post("/episodes/{episode_id}/analysis/character", status_code=202)
def start_character_analysis(episode_id: str, payload: StartCharacterAnalysisRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "stage_name": "character_analysis",
            "state": "needs_review",
            "source_video": payload.source_video,
        },
    }


@router.post("/episodes/{episode_id}/analysis/character/approve")
def approve_character_analysis(episode_id: str, payload: ApproveCharacterAnalysisRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "state": "approved",
            "approved_characters": [item.model_dump() for item in payload.approved_characters],
        },
    }
```

Wire in `apps/backend/app/main.py`:

```python
from app.api.routes.analysis import router as analysis_router
app.include_router(analysis_router, prefix="/api/v1")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_character_analysis_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes/analysis.py apps/backend/app/main.py apps/backend/tests/api/test_character_analysis_api.py
git commit -m "feat(api): add character analysis review gate"
```

### Task 9: Generation and Segment Regeneration APIs

**Files:**
- Create: `apps/backend/app/api/routes/generation.py`
- Create: `apps/backend/app/api/routes/review.py`
- Modify: `apps/backend/app/main.py`
- Create: `apps/backend/tests/api/test_generation_review_api.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/api/test_generation_review_api.py
def test_start_generation_after_character_approval(client):
    response = client.post("/api/v1/episodes/episode_1/generation", json={"approved": True})
    assert response.status_code == 202
    assert response.json()["data"]["stage_name"] == "episode_generation"


def test_regenerate_segment_accepts_director_overrides(client):
    response = client.post(
        "/api/v1/episodes/episode_1/segments/seg_1/regenerate",
        json={"dub_text": "我不会再逃了。", "emotion": "坚定", "reference_sample_id": "sample_1"},
    )
    assert response.status_code == 202
    assert response.json()["data"]["segment_id"] == "seg_1"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_generation_review_api.py -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/api/routes/generation.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class StartGenerationRequest(BaseModel):
    approved: bool


@router.post("/episodes/{episode_id}/generation", status_code=202)
def start_generation(episode_id: str, payload: StartGenerationRequest):
    state = "running" if payload.approved else "blocked"
    return {"success": payload.approved, "data": {"episode_id": episode_id, "stage_name": "episode_generation", "state": state}}
```

```python
# apps/backend/app/api/routes/review.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RegenerateSegmentRequest(BaseModel):
    dub_text: str
    emotion: str
    reference_sample_id: str


@router.post("/episodes/{episode_id}/segments/{segment_id}/regenerate", status_code=202)
def regenerate_segment(episode_id: str, segment_id: str, payload: RegenerateSegmentRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "segment_id": segment_id,
            "state": "running",
            "dub_text": payload.dub_text,
            "emotion": payload.emotion,
            "reference_sample_id": payload.reference_sample_id,
        },
    }
```

Wire both routers in `apps/backend/app/main.py`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_generation_review_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes apps/backend/app/main.py apps/backend/tests/api/test_generation_review_api.py
git commit -m "feat(api): add episode generation and segment regeneration"
```

## Phase 5: Worker Generation Contracts

### Task 10: Dub Script and Segment Direction Contracts

**Files:**
- Create: `apps/worker/worker/pipelines/dub_script.py`
- Create: `apps/worker/worker/pipelines/segment_direction.py`
- Create: `tests/unit/test_generation_contracts.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_generation_contracts.py
from worker.pipelines.dub_script import rewrite_for_dubbing
from worker.pipelines.segment_direction import build_segment_direction


def test_rewrite_for_dubbing_respects_character_style():
    result = rewrite_for_dubbing(
        source_text="ありがとう",
        literal_translation="谢谢",
        character_style={"base_tone": "温柔但坚定", "speech_rate": "中速"},
        duration_ms=1200,
    )
    assert result["dub_text"]
    assert result["style_hint"] == "温柔但坚定"


def test_segment_direction_contains_performance_controls():
    direction = build_segment_direction(segment_id="seg_1", emotion="紧张", intensity=0.7, duration_target_ms=1500)
    assert direction["emotion"] == "紧张"
    assert direction["duration_target_ms"] == 1500
```

**Step 2: Run test to verify it fails**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_generation_contracts.py -v`  
Expected: FAIL because modules do not exist.

**Step 3: Write minimal implementation**

```python
# apps/worker/worker/pipelines/dub_script.py
def rewrite_for_dubbing(source_text: str, literal_translation: str, character_style: dict[str, object], duration_ms: int):
    return {
        "source_text": source_text,
        "literal_translation": literal_translation,
        "dub_text": literal_translation,
        "duration_target_ms": duration_ms,
        "style_hint": str(character_style.get("base_tone", "")),
    }
```

```python
# apps/worker/worker/pipelines/segment_direction.py
def build_segment_direction(segment_id: str, emotion: str, intensity: float, duration_target_ms: int):
    return {
        "segment_id": segment_id,
        "emotion": emotion,
        "intensity": intensity,
        "duration_target_ms": duration_target_ms,
        "speech_rate": "auto",
        "pause_style": "source_guided",
    }
```

**Step 4: Run test to verify it passes**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit/test_generation_contracts.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/pipelines tests/unit/test_generation_contracts.py
git commit -m "feat(worker): add generation pipeline contracts"
```

## Phase 6: Web Director Console MVP

### Task 11: Web App Shell and Review Pages

**Files:**
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/app/episodes/[episodeId]/character-review/page.tsx`
- Create: `apps/web/app/episodes/[episodeId]/segments/page.tsx`
- Create: `apps/web/next.config.mjs`
- Create: `apps/web/tsconfig.json`
- Modify: `apps/web/package.json`

**Step 1: Write the failing smoke script**

Update `apps/web/package.json`:

```json
"test:e2e": "node -e \"const fs=require('fs');const checks=[['app/page.tsx','AI 配音导演台'],['app/episodes/[episodeId]/character-review/page.tsx','角色分析确认'],['app/episodes/[episodeId]/segments/page.tsx','关键片段精修']];for(const [f,t] of checks){if(!fs.existsSync(f)){console.error('Missing file:',f);process.exit(1)};if(!fs.readFileSync(f,'utf8').includes(t)){console.error('Missing text:',t);process.exit(1)}};console.log('web smoke ok')\""
```

**Step 2: Run test to verify it fails**

Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL because app pages do not exist.

**Step 3: Write minimal implementation**

Create pages containing the required titles:

```tsx
// apps/web/app/page.tsx
export default function HomePage() {
  return (
    <main>
      <h1>AI 配音导演台</h1>
      <p>按单集生产，按整季沉淀角色资产。</p>
    </main>
  );
}
```

```tsx
// apps/web/app/episodes/[episodeId]/character-review/page.tsx
export default async function CharacterReviewPage({ params }: { params: Promise<{ episodeId: string }> }) {
  const { episodeId } = await params;
  return (
    <main>
      <p>Episode: {episodeId}</p>
      <h1>角色分析确认</h1>
    </main>
  );
}
```

```tsx
// apps/web/app/episodes/[episodeId]/segments/page.tsx
export default async function SegmentRefinementPage({ params }: { params: Promise<{ episodeId: string }> }) {
  const { episodeId } = await params;
  return (
    <main>
      <p>Episode: {episodeId}</p>
      <h1>关键片段精修</h1>
    </main>
  );
}
```

Create a simple `layout.tsx`, `globals.css`, `next.config.mjs`, and `tsconfig.json`.

**Step 4: Run test to verify it passes**

Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web smoke ok`.

**Step 5: Commit**

```bash
git add apps/web
git commit -m "feat(web): add director console mvp screens"
```

## Phase 7: Final Verification and Handoff

### Task 12: Full Verification Gate

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-04-16-ai-dubbing-director-console-verification.md`

**Step 1: Run backend tests**

Run: `python -m pytest -q apps/backend/tests`  
Expected: PASS.

**Step 2: Run worker/root tests**

Run: `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit`  
Expected: PASS.

**Step 3: Run web smoke tests**

Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS.

**Step 4: Update README**

Add:

Add a `开发命令` section containing these commands:

```powershell
npm run dev:backend
npm run dev:worker
npm run dev:web
python -m pytest -q apps/backend/tests
$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Record verification evidence**

Create `docs/plans/2026-04-16-ai-dubbing-director-console-verification.md` with the command outputs and status.

**Step 6: Commit**

```bash
git add README.md docs/plans/2026-04-16-ai-dubbing-director-console-verification.md
git commit -m "docs: record director console mvp verification"
```

## Post-MVP Real Model Integration Order

Do not integrate real models until the deterministic MVP passes.

1. `media_ingest`: FFmpeg extraction and normalization.
2. `audio_separation`: Demucs or UVR-compatible local adapter.
3. `asr_align`: Whisper-compatible ASR adapter.
4. `speaker_role`: diarization and speaker embedding adapter.
5. `dub_script`: Qwen primary and Doubao fallback LLM adapters.
6. `tts_synthesis`: provider or local TTS adapter supporting reference audio.
7. `mix_master`: FFmpeg-based mix/export adapter.

Each adapter must preserve the deterministic contract and ship fake-provider tests first.
