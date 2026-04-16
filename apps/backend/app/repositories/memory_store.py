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