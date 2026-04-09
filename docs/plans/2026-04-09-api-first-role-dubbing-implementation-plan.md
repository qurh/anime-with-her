# API-First Role Dubbing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an API-first anime dubbing system with mandatory role-based tracks (`max_speakers=4`), provider fallback (Qwen primary, Doubao secondary), budget guardrails, voice registry, full rerender, and version/log retention policies.

**Architecture:** The backend orchestrates jobs, budget policy, state transitions, and versioning. A worker executes pipeline stages and emits structured manifests/artifacts. The web console remains thin and consumes backend APIs for job status, budget decisions, and voice profile management.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, SQLModel/SQLite (phase 1), pytest, httpx TestClient, APScheduler (or lightweight internal scheduler), Node/Next.js for optional web console.

---

## Execution Rules

- Use `@superpowers:test-driven-development` for every implementation task.
- Use `@superpowers:verification-before-completion` before claiming each task complete.
- Keep changes DRY and YAGNI; implement only what each test requires.
- Commit after each task.

### Task 1: Backend Bootstrap and Health API

**Files:**
- Create: `apps/backend/pyproject.toml`
- Create: `apps/backend/app/__init__.py`
- Create: `apps/backend/app/main.py`
- Create: `apps/backend/app/api/routes/health.py`
- Create: `apps/backend/tests/conftest.py`
- Test: `apps/backend/tests/api/test_health.py`

**Step 1: Write the failing test**

```python
# apps/backend/tests/api/test_health.py
def test_health_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_health.py::test_health_ok -v`  
Expected: FAIL with import/app creation errors.

**Step 3: Write minimal implementation**

```python
# apps/backend/app/main.py
from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI()
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

Run: `python -m pytest -q apps/backend/tests/api/test_health.py::test_health_ok -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/pyproject.toml apps/backend/app apps/backend/tests
git commit -m "feat(backend): bootstrap FastAPI app with health endpoint"
```

### Task 2: Job Domain Models and State Enum

**Files:**
- Create: `apps/backend/app/domain/job.py`
- Create: `apps/backend/app/db/models.py`
- Create: `apps/backend/app/db/session.py`
- Test: `apps/backend/tests/unit/test_job_state.py`

**Step 1: Write the failing test**

```python
def test_job_state_transitions_allow_happy_path():
    from app.domain.job import JobState, can_transition
    assert can_transition(JobState.CREATED, JobState.RUNNING) is True
    assert can_transition(JobState.RUNNING, JobState.DONE) is True
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_job_state.py::test_job_state_transitions_allow_happy_path -v`  
Expected: FAIL with missing module/function.

**Step 3: Write minimal implementation**

```python
from enum import Enum

class JobState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PARTIAL_DONE = "partial_done"
    DONE = "done"
    FAILED = "failed"
    AWAITING_BUDGET_DECISION = "awaiting_budget_decision"
    RERENDERING = "rerendering"

_ALLOWED = {
    JobState.CREATED: {JobState.RUNNING, JobState.FAILED},
    JobState.RUNNING: {JobState.PARTIAL_DONE, JobState.DONE, JobState.FAILED, JobState.AWAITING_BUDGET_DECISION},
}

def can_transition(src: JobState, dst: JobState) -> bool:
    return dst in _ALLOWED.get(src, set())
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_job_state.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/domain apps/backend/app/db apps/backend/tests/unit/test_job_state.py
git commit -m "feat(backend): add job state domain model and transition rules"
```

### Task 3: Provider Contracts and Routing (Qwen Primary, Doubao Fallback)

**Files:**
- Create: `apps/backend/app/providers/contracts.py`
- Create: `apps/backend/app/providers/qwen_adapter.py`
- Create: `apps/backend/app/providers/doubao_adapter.py`
- Create: `apps/backend/app/providers/router.py`
- Test: `apps/backend/tests/unit/test_provider_router.py`

**Step 1: Write the failing test**

```python
def test_router_falls_back_to_secondary_when_primary_fails():
    from app.providers.router import ProviderRouter
    result = ProviderRouter(primary_fail=True).translate("こんにちは")
    assert result.provider == "doubao"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_provider_router.py::test_router_falls_back_to_secondary_when_primary_fails -v`  
Expected: FAIL with missing router.

**Step 3: Write minimal implementation**

```python
class ProviderResult:
    def __init__(self, text: str, provider: str):
        self.text = text
        self.provider = provider

class ProviderRouter:
    def __init__(self, primary_fail: bool = False):
        self.primary_fail = primary_fail

    def translate(self, text: str) -> ProviderResult:
        if self.primary_fail:
            return ProviderResult("你好", "doubao")
        return ProviderResult("你好", "qwen")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_provider_router.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/providers apps/backend/tests/unit/test_provider_router.py
git commit -m "feat(backend): add provider contracts and qwen->doubao fallback router"
```

### Task 4: Budget Policy (¥5 Cap, 10-Minute Timeout Default Action)

**Files:**
- Create: `apps/backend/app/services/budget_service.py`
- Create: `apps/backend/app/domain/budget.py`
- Test: `apps/backend/tests/unit/test_budget_policy.py`

**Step 1: Write the failing test**

```python
def test_budget_timeout_defaults_to_skip_lipsync():
    from app.services.budget_service import resolve_timeout_action
    assert resolve_timeout_action(waited_minutes=10) == "skip_lipsync_continue_dubbing"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_budget_policy.py::test_budget_timeout_defaults_to_skip_lipsync -v`  
Expected: FAIL with missing service.

**Step 3: Write minimal implementation**

```python
BUDGET_CAP_CNY = 5.0
TIMEOUT_MINUTES = 10

def resolve_timeout_action(waited_minutes: int) -> str:
    if waited_minutes >= TIMEOUT_MINUTES:
        return "skip_lipsync_continue_dubbing"
    return "await_user_choice"
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_budget_policy.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/services/budget_service.py apps/backend/app/domain/budget.py apps/backend/tests/unit/test_budget_policy.py
git commit -m "feat(backend): implement budget cap policy and timeout default action"
```

### Task 5: Job Submission and Query APIs

**Files:**
- Create: `apps/backend/app/api/schemas/jobs.py`
- Create: `apps/backend/app/api/routes/jobs.py`
- Modify: `apps/backend/app/main.py`
- Test: `apps/backend/tests/api/test_jobs_api.py`

**Step 1: Write the failing test**

```python
def test_create_job_returns_created_state(client):
    resp = client.post("/api/v1/jobs", json={"input_video": "data/input/a.mp4"})
    assert resp.status_code == 201
    assert resp.json()["data"]["state"] == "created"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_jobs_api.py::test_create_job_returns_created_state -v`  
Expected: FAIL with 404 or missing schema.

**Step 3: Write minimal implementation**

```python
@router.post("/jobs", status_code=201)
def create_job(payload: CreateJobRequest):
    return {"success": True, "data": {"job_id": "job_1", "state": "created"}}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_jobs_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api apps/backend/app/main.py apps/backend/tests/api/test_jobs_api.py
git commit -m "feat(api): add job creation and query endpoints"
```

### Task 6: Worker Skeleton and Stage Manifest

**Files:**
- Create: `apps/worker/pyproject.toml`
- Create: `apps/worker/worker/main.py`
- Create: `apps/worker/worker/pipeline.py`
- Create: `apps/worker/worker/manifest.py`
- Test: `tests/unit/test_worker_manifest.py`

**Step 1: Write the failing test**

```python
def test_manifest_contains_stage_and_artifact_paths():
    from worker.manifest import build_stage_manifest
    m = build_stage_manifest("job_1", "asr", ["data/intermediate/job_1/asr.json"])
    assert m["stage"] == "asr"
    assert len(m["artifacts"]) == 1
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_worker_manifest.py::test_manifest_contains_stage_and_artifact_paths -v`  
Expected: FAIL with missing package.

**Step 3: Write minimal implementation**

```python
def build_stage_manifest(job_id: str, stage: str, artifacts: list[str]) -> dict:
    return {"job_id": job_id, "stage": stage, "artifacts": artifacts}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_worker_manifest.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker tests/unit/test_worker_manifest.py
git commit -m "feat(worker): add pipeline skeleton and stage manifest builder"
```

### Task 7: Role-Based Speaker Mapping (`max_speakers=4`)

**Files:**
- Create: `apps/worker/worker/speaker_mapper.py`
- Create: `apps/worker/worker/types.py`
- Test: `tests/unit/test_speaker_mapper.py`

**Step 1: Write the failing test**

```python
def test_mapper_caps_roles_at_four():
    from worker.speaker_mapper import SpeakerMapper
    mapper = SpeakerMapper(max_speakers=4)
    ids = [mapper.assign(f"spk_{i}") for i in range(1, 7)]
    assert max(ids) <= 4
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_speaker_mapper.py::test_mapper_caps_roles_at_four -v`  
Expected: FAIL with missing mapper.

**Step 3: Write minimal implementation**

```python
class SpeakerMapper:
    def __init__(self, max_speakers: int = 4):
        self.max_speakers = max_speakers
        self._map = {}
        self._next = 1

    def assign(self, raw_id: str) -> int:
        if raw_id in self._map:
            return self._map[raw_id]
        if self._next <= self.max_speakers:
            self._map[raw_id] = self._next
            self._next += 1
        else:
            self._map[raw_id] = self.max_speakers
        return self._map[raw_id]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_speaker_mapper.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/speaker_mapper.py apps/worker/worker/types.py tests/unit/test_speaker_mapper.py
git commit -m "feat(worker): enforce role-based speaker mapping with max_speakers=4"
```

### Task 8: Series Voice Registry (Auto Collect + Manual Replace)

**Files:**
- Create: `apps/backend/app/api/routes/voice_registry.py`
- Create: `apps/backend/app/api/schemas/voice_registry.py`
- Create: `apps/backend/app/services/voice_registry_service.py`
- Test: `apps/backend/tests/api/test_voice_registry_api.py`

**Step 1: Write the failing test**

```python
def test_create_voice_profile_version(client):
    payload = {"series": "Naruto", "character": "Kakashi", "sample_path": "data/intermediate/job_1/kakashi.wav"}
    resp = client.post("/api/v1/voice-registry/versions", json=payload)
    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "auto_collected"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_voice_registry_api.py::test_create_voice_profile_version -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
@router.post("/voice-registry/versions", status_code=201)
def create_version(payload: CreateVoiceVersionRequest):
    return {"success": True, "data": {"version_id": "v1", "status": "auto_collected"}}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_voice_registry_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes/voice_registry.py apps/backend/app/api/schemas/voice_registry.py apps/backend/app/services/voice_registry_service.py apps/backend/tests/api/test_voice_registry_api.py
git commit -m "feat(api): add series voice registry version endpoints"
```

### Task 9: Full Rerender Trigger After Voice Replacement

**Files:**
- Create: `apps/backend/app/api/routes/rerender.py`
- Create: `apps/backend/app/services/rerender_service.py`
- Test: `apps/backend/tests/api/test_rerender_api.py`

**Step 1: Write the failing test**

```python
def test_rerender_starts_new_job_after_voice_update(client):
    resp = client.post("/api/v1/rerender", json={"source_job_id": "job_1", "voice_version_id": "v2"})
    assert resp.status_code == 202
    assert resp.json()["data"]["state"] == "rerendering"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_rerender_api.py::test_rerender_starts_new_job_after_voice_update -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
@router.post("/rerender", status_code=202)
def rerender(payload: RerenderRequest):
    return {"success": True, "data": {"job_id": "job_r1", "state": "rerendering"}}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_rerender_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes/rerender.py apps/backend/app/services/rerender_service.py apps/backend/tests/api/test_rerender_api.py
git commit -m "feat(api): trigger full rerender workflow after voice replacement"
```

### Task 10: Output Version Retention (Keep Latest 2)

**Files:**
- Create: `apps/backend/app/services/version_retention_service.py`
- Test: `apps/backend/tests/unit/test_version_retention.py`

**Step 1: Write the failing test**

```python
def test_retention_keeps_latest_two_versions():
    from app.services.version_retention_service import retained_versions
    versions = ["v1", "v2", "v3"]
    assert retained_versions(versions) == ["v2", "v3"]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_version_retention.py::test_retention_keeps_latest_two_versions -v`  
Expected: FAIL with missing service.

**Step 3: Write minimal implementation**

```python
def retained_versions(versions: list[str]) -> list[str]:
    return versions[-2:]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_version_retention.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/services/version_retention_service.py apps/backend/tests/unit/test_version_retention.py
git commit -m "feat(backend): add output version retention policy keep-latest-2"
```

### Task 11: Audit Log TTL Cleanup (30 Days Hard Delete)

**Files:**
- Create: `apps/backend/app/services/audit_log_service.py`
- Create: `scripts/cleanup-audit-logs.ps1`
- Test: `apps/backend/tests/unit/test_audit_log_cleanup.py`

**Step 1: Write the failing test**

```python
def test_cleanup_deletes_records_older_than_30_days():
    from app.services.audit_log_service import should_delete
    assert should_delete(record_age_days=31) is True
    assert should_delete(record_age_days=30) is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/unit/test_audit_log_cleanup.py::test_cleanup_deletes_records_older_than_30_days -v`  
Expected: FAIL with missing module.

**Step 3: Write minimal implementation**

```python
TTL_DAYS = 30

def should_delete(record_age_days: int) -> bool:
    return record_age_days > TTL_DAYS
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/unit/test_audit_log_cleanup.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/services/audit_log_service.py scripts/cleanup-audit-logs.ps1 apps/backend/tests/unit/test_audit_log_cleanup.py
git commit -m "feat(ops): add 30-day audit log hard-delete cleanup policy"
```

### Task 12: Budget Decision API (Two Options + Cost Estimate)

**Files:**
- Create: `apps/backend/app/api/routes/budget.py`
- Create: `apps/backend/app/api/schemas/budget.py`
- Modify: `apps/backend/app/services/budget_service.py`
- Test: `apps/backend/tests/api/test_budget_decision_api.py`

**Step 1: Write the failing test**

```python
def test_budget_decision_payload_contains_two_options_and_estimate(client):
    resp = client.get("/api/v1/jobs/job_1/budget-decision")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "skip_lipsync_continue_dubbing" in data["options"]
    assert "continue_full_pipeline" in data["options"]
    assert data["estimated_extra_cost_cny"] >= 0
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_budget_decision_api.py::test_budget_decision_payload_contains_two_options_and_estimate -v`  
Expected: FAIL with 404.

**Step 3: Write minimal implementation**

```python
@router.get("/jobs/{job_id}/budget-decision")
def budget_decision(job_id: str):
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "options": ["skip_lipsync_continue_dubbing", "continue_full_pipeline"],
            "estimated_extra_cost_cny": 1.25,
            "timeout_minutes": 10,
            "default_action": "skip_lipsync_continue_dubbing",
        },
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_budget_decision_api.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes/budget.py apps/backend/app/api/schemas/budget.py apps/backend/app/services/budget_service.py apps/backend/tests/api/test_budget_decision_api.py
git commit -m "feat(api): add budget decision endpoint with options and extra cost estimate"
```

### Task 13: End-to-End API Integration for Fast Deliverable

**Files:**
- Create: `apps/backend/tests/integration/test_fast_deliverable_flow.py`
- Modify: `apps/backend/tests/conftest.py`

**Step 1: Write the failing test**

```python
def test_fast_flow_reaches_partial_or_done(client):
    create = client.post("/api/v1/jobs", json={"input_video": "data/input/demo.mp4"})
    job_id = create.json()["data"]["job_id"]
    status = client.get(f"/api/v1/jobs/{job_id}")
    assert status.status_code == 200
    assert status.json()["data"]["state"] in {"running", "partial_done", "done"}
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/integration/test_fast_deliverable_flow.py::test_fast_flow_reaches_partial_or_done -v`  
Expected: FAIL until routing/storage wires are in place.

**Step 3: Write minimal implementation**

```python
# Add in-memory repository in conftest/main wiring for jobs
# Keep implementation minimal: create -> created, query -> created/running
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/integration/test_fast_deliverable_flow.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/tests/integration/test_fast_deliverable_flow.py apps/backend/tests/conftest.py
git commit -m "test(integration): verify fast deliverable job flow"
```

### Task 14: Optional Web Console Skeleton (Job List + Budget Decision Panel)

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/lib/api.ts`
- Create: `apps/web/app/budget/[jobId]/page.tsx`
- Test: `tests/e2e/web-smoke.spec.ts`

**Step 1: Write the failing test**

```ts
test("home renders job list header", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Jobs")).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test:e2e`  
Expected: FAIL because app/pages are missing.

**Step 3: Write minimal implementation**

```tsx
export default function Home() {
  return <main><h1>Jobs</h1></main>;
}
```

**Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test:e2e`  
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/web tests/e2e/web-smoke.spec.ts
git commit -m "feat(web): add minimal console for jobs and budget decision entry"
```

### Task 15: Root Scripts and Developer Workflow

**Files:**
- Create: `package.json`
- Create: `scripts/dev-backend.ps1`
- Create: `scripts/dev-worker.ps1`
- Create: `scripts/dev-web.ps1`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
def test_root_scripts_are_declared():
    import json, pathlib
    data = json.loads(pathlib.Path("package.json").read_text(encoding="utf-8"))
    assert "dev:backend" in data["scripts"]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_root_scripts.py::test_root_scripts_are_declared -v`  
Expected: FAIL because `package.json` is missing.

**Step 3: Write minimal implementation**

```json
{
  "name": "anime-with-her-monorepo",
  "private": true,
  "scripts": {
    "dev:backend": "uvicorn app.main:app --reload --app-dir apps/backend",
    "test:backend": "python -m pytest -q apps/backend/tests"
  }
}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_root_scripts.py -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add package.json scripts README.md tests/unit/test_root_scripts.py
git commit -m "chore(repo): add root dev scripts and onboarding commands"
```

### Task 16: Final Verification Gate

**Files:**
- Modify: `docs/plans/2026-04-09-api-first-role-dubbing-implementation-plan.md` (checklist updates only)

**Step 1: Run full backend test suite**

Run: `python -m pytest -q apps/backend/tests`  
Expected: PASS.

**Step 2: Run worker and root tests**

Run: `python -m pytest -q tests/unit tests/integration`  
Expected: PASS.

**Step 3: Run optional web checks (if implemented)**

Run: `npm --prefix apps/web run lint && npm --prefix apps/web run test:e2e`  
Expected: PASS.

**Step 4: Verify git status clean**

Run: `git status --short`  
Expected: no unexpected changes.

**Step 5: Commit verification evidence**

```bash
git add docs/plans/2026-04-09-api-first-role-dubbing-implementation-plan.md
git commit -m "docs(plan): record verification completion checklist"
```

## Handoff Notes

- Start implementation in a dedicated worktree.
- Keep all provider secrets in environment variables only.
- Do not block fast deliverable on lipsync stage.
- Ensure budget decision UI/API always exposes the two approved options and estimated extra cost.

