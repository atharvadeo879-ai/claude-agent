"""Phase 3: edit and revision history workflow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Revision:
    revision_id: int
    revision_type: str
    content: str


class RevisionManager:
    def __init__(self) -> None:
        self._history: dict[str, list[Revision]] = {}

    def add_revision(self, response_id: str, revision_type: str, content: str) -> Revision:
        if revision_type not in {"prompt_edit", "response_edit"}:
            raise ValueError("revision_type must be prompt_edit or response_edit")
        history = self._history.setdefault(response_id, [])
        rev = Revision(revision_id=len(history) + 1, revision_type=revision_type, content=content)
        history.append(rev)
        return rev

    def get_history(self, response_id: str) -> list[Revision]:
        return list(self._history.get(response_id, []))

