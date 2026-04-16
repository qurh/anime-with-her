from app.domain.models import Episode, EpisodeState, SeasonCharacterProfile, StageState


def test_episode_defaults_to_draft_state():
    episode = Episode(
        episode_id="ep_001",
        series_id="series_001",
        season_id="season_001",
        title="第1集",
    )
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
