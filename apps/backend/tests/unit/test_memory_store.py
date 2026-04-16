from app.repositories.memory_store import MemoryStore


def test_store_creates_series_season_episode():
    store = MemoryStore()
    series = store.create_series(title="示例动漫")
    season = store.create_season(series.series_id, title="第一季")
    episode = store.create_episode(series.series_id, season.season_id, title="第1集")

    assert series.series_id.startswith("series_")
    assert season.series_id == series.series_id
    assert episode.season_id == season.season_id
