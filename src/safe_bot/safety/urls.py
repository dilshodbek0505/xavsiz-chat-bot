import re
from urllib.parse import urlsplit

_URL_RE = re.compile(r"(?i)\b(?:https?|javascript|file|intent|data):[^\s<>'\"]+")
_WEB_ADDRESS = re.compile(r"(?i)^(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?(?:[/?#].*)?$")


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


def canonical_url(url: str) -> str | None:
    """Havolani tekshiruv uchun tayyorlaydi.

    Telegram oddiy havolani `https://` siz (`google.com`, `t.me/kanal`) yoki
    `//host` ko'rinishida berishi mumkin. Bunday manzil oddiy veb havola.
    Faqat aniq bo'lmagan matn `None` qaytadi va o'chirilmaydi.
    """
    raw = url.strip()
    if not raw:
        return None
    if raw.startswith("//"):
        raw = "https:" + raw
    if urlsplit(raw).scheme:
        return raw
    if _WEB_ADDRESS.match(raw):
        return "https://" + raw
    return None
