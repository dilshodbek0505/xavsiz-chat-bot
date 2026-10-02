from dataclasses import dataclass
from urllib.parse import urlsplit

from safe_bot.safety.models import Decision
from safe_bot.safety.notice import reason_line
from safe_bot.safety.urls import canonical_url


@dataclass(frozen=True, slots=True)
class AlertSource:
    chat_id: int
    chat_name: str
    chat_username: str | None
    sender_name: str
    sender_username: str | None
    file_name: str | None
    hosts: tuple[str, ...]


def build_business_alert(source: AlertSource, decision: Decision, *, deleted: bool) -> str:
    if deleted:
        head = "Xavfli xabar topildi va o'chirildi."
    else:
        head = "Xavfli xabar topildi. O'chirib bo'lmadi."

    lines = [
        head,
        "",
        f"Chat: {_with_username(source.chat_name, source.chat_username)}",
        f"Chat ID: {source.chat_id}",
        f"Yuboruvchi: {_with_username(source.sender_name, source.sender_username)}",
    ]
    if source.file_name:
        lines.append(f"Fayl: {source.file_name}")
    if source.hosts:
        lines.append("Havola: " + ", ".join(source.hosts))
    if decision.reasons:
        lines.append("Sabab:")
        lines.extend(f"— {reason_line(reason)}" for reason in decision.reasons)
    if not deleted:
        lines.append("")
        lines.append("Telegram Business sozlamasida barcha xabarlarni o'chirish ruxsati kerak.")
    return "\n".join(lines)


def hosts_from_urls(urls: tuple[str, ...]) -> tuple[str, ...]:
    hosts: list[str] = []
    seen: set[str] = set()
    for url in urls:
        prepared = canonical_url(url)
        if prepared is None:
            continue
        host = urlsplit(prepared).hostname
        if not host:
            continue
        normalized = host.lower().removeprefix("www.")
        if normalized in seen:
            continue
        seen.add(normalized)
        hosts.append(normalized)
    return tuple(hosts)


def _with_username(name: str, username: str | None) -> str:
    label = name.strip() or "noma'lum"
    if username:
        return f"{label} (@{username.removeprefix('@')})"
    return label
