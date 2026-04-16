def test_create_series_season_episode(client):
    series = client.post("/api/v1/series", json={"title": "示例动漫"})
    assert series.status_code == 201
    series_id = series.json()["data"]["series_id"]

    season = client.post(f"/api/v1/series/{series_id}/seasons", json={"title": "第一季"})
    assert season.status_code == 201
    season_id = season.json()["data"]["season_id"]

    episode = client.post(
        f"/api/v1/series/{series_id}/seasons/{season_id}/episodes",
        json={"title": "第1集"},
    )
    assert episode.status_code == 201
    assert episode.json()["data"]["episode_id"].startswith("episode_")
