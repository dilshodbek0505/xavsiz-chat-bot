from safe_bot.safety.models import Decision, Reason

SAFE_NOTICE = "Tekshirildi. Xavfli narsa topilmadi."

_REASON_TEXT = {
    "blocked_domain": "Havola bloklangan ro'yxatda",
    "blocked_hash": "Fayl xeshi bloklangan ro'yxatda",
    "ip_host": "Havola IP manzilga olib boradi",
    "url_userinfo": "Havolada foydalanuvchi yoki parol bor",
    "app_url": "Havola ilova faylini yuklab oladi",
    "unsafe_scheme": "Havola xavfli protokolda",
    "app_file": "Ilova fayli tashqi tekshiruvsiz xavfli deb olindi",
    "external_malicious_url": "Tashqi tekshiruv havolani zararli deb topdi",
    "external_malicious_file": "Tashqi tekshiruv faylni zararli deb topdi",
    "external_unknown_file": "Ilova fayli tashqi bazada toza deb topilmadi",
    "external_error_file": "Tashqi tekshiruv ishlamadi, ilova fayli o'chirildi",
    "file_too_large": "Ilova fayli juda katta, tekshirib bo'lmadi",
    "hash_unavailable": "Ilova faylining xeshi olinmadi",
}


def deletion_notice(decision: Decision) -> str:
    lines = ["Xavfli material topildi. Xabar o'chirildi."]
    for reason in decision.reasons:
        lines.append(f"— {reason_line(reason)}")
    return "\n".join(lines)


def reason_line(reason: Reason) -> str:
    text = _REASON_TEXT.get(reason.code, reason.code)
    detail = reason.detail.strip()
    if detail:
        return f"{text}: {detail}"
    return text
