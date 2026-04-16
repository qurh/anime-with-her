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