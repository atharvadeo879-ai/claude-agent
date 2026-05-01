"""Phase 1: foundation primitives and output shaping."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptRequest:
    user_id: str
    prompt: str


def validate_request(request: PromptRequest) -> None:
    if not request.user_id.strip():
        raise ValueError("user_id is required")
    if len(request.prompt.strip()) < 10:
        raise ValueError("prompt must be at least 10 characters")


class ArchitectureFormatter:
    """Normalizes generated content into architecture sections."""

    sections = ("Overview", "Components", "Data Flow", "Risks", "Next Steps")

    def format(self, body: str) -> dict[str, str]:
        text = body.strip()
        if not text:
            raise ValueError("body must not be empty")
        return {section: f"{section}: {text}" for section in self.sections}

