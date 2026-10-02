from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Reason:
    code: str
    detail: str = ""


@dataclass(frozen=True, slots=True)
class Submission:
    """Tekshiriladigan xabar: havolalar va, bo'lsa, bitta fayl."""

    urls: tuple[str, ...] = ()
    file_name: str | None = None
    mime_type: str | None = None
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class Decision:
    delete: bool
    reasons: tuple[Reason, ...] = ()
