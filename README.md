# anime-with-her

API-first anime dubbing monorepo with role-based speaker pipeline.

## Structure

- `apps/backend`: FastAPI orchestration API
- `apps/worker`: worker skeleton and pipeline utilities
- `apps/web`: minimal console skeleton
- `docs`: architecture and implementation plans

## Common Commands

```powershell
npm run dev:backend
npm run dev:worker
npm run dev:web
npm run test:backend
```

## Frontend Quick Start

```powershell
npm --prefix apps/web install
npm run dev:web
```

Web console: `http://127.0.0.1:3000`

