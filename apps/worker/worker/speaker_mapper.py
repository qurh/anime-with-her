from .types import RoleId


class SpeakerMapper:
    def __init__(self, max_speakers: int = 4):
        self.max_speakers = max_speakers
        self._mapping: dict[str, RoleId] = {}
        self._next_role_id = 1

    def assign(self, raw_id: str) -> RoleId:
        if raw_id in self._mapping:
            return self._mapping[raw_id]

        if self._next_role_id <= self.max_speakers:
            role_id: RoleId = RoleId(self._next_role_id)
            self._mapping[raw_id] = role_id
            self._next_role_id += 1
            return role_id

        fallback_role: RoleId = RoleId(self.max_speakers)
        self._mapping[raw_id] = fallback_role
        return fallback_role
