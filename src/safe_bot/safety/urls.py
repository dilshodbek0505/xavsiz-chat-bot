import re

_URL_RE = re.compile(r"(?i)\b(?:https?|javascript|file|intent|data):[^\s<>'\"]+")


def extract_urls(text: str) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()
    for match in _URL_RE.findall(text):
        cleaned = match.rstrip(".,);]>'\"")
        if cleaned in seen:
            continue
        seen.add(cleaned)
        found.append(cleaned)
    return tuple(found)
