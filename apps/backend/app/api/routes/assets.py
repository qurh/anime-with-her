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
