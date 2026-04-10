from __future__ import annotations

from pathlib import Path


def test_upload_video_saves_file_and_returns_path(client, monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("ANIME_WITH_HER_UPLOAD_DIR", str(upload_dir))

    resp = client.post(
        "/api/v1/uploads/video",
        content=b"fake-video-bytes",
        headers={
            "content-type": "video/mp4",
            "x-filename": "episode-01.mp4",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    stored_path = body["data"]["stored_path"]
    assert body["data"]["original_filename"] == "episode-01.mp4"
    assert body["data"]["size_bytes"] == len(b"fake-video-bytes")

    expected_file = Path(stored_path)
    if not expected_file.is_absolute():
        expected_file = Path.cwd() / stored_path
    assert expected_file.exists()


def test_upload_video_rejects_non_video_content_type(client):
    resp = client.post(
        "/api/v1/uploads/video",
        content=b"not-video",
        headers={
            "content-type": "application/json",
            "x-filename": "not-video.json",
        },
    )

    assert resp.status_code == 415
