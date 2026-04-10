def test_mapper_caps_roles_at_four():
    from apps.worker.worker.speaker_mapper import SpeakerMapper

    mapper = SpeakerMapper(max_speakers=4)
    ids = [mapper.assign(f"spk_{i}") for i in range(1, 7)]

    assert max(ids) <= 4
