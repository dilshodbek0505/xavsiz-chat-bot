from safe_bot.safety.alert import AlertSource, build_business_alert, hosts_from_urls
from safe_bot.safety.models import Decision, Reason


def test_alert_names_chat_sender_and_avoids_clickable_url() -> None:
    text = build_business_alert(
        AlertSource(
            chat_id=99,
            chat_name="Ali Valiyev",
            chat_username="ali",
            sender_name="Ali Valiyev",
            sender_username="ali",
            file_name="app.apk",
            hosts=("phishing.test",),
        ),
        Decision(delete=True, reasons=(Reason("blocked_domain", "phishing.test"),)),
        deleted=True,
    )

    assert "o'chirildi" in text
    assert "Ali Valiyev (@ali)" in text
    assert "Chat ID: 99" in text
    assert "app.apk" in text
    assert "phishing.test" in text
    assert "http" not in text


def test_alert_explains_when_delete_permission_is_missing() -> None:
    text = build_business_alert(
        AlertSource(
            chat_id=5,
            chat_name="Gulnora",
            chat_username=None,
            sender_name="Gulnora",
            sender_username=None,
            file_name=None,
            hosts=("203.0.113.10",),
        ),
        Decision(delete=True, reasons=(Reason("ip_host", "203.0.113.10"),)),
        deleted=False,
    )

    assert "O'chirib bo'lmadi" in text
    assert "ruxsat" in text


def test_hosts_drop_scheme_and_www() -> None:
    assert hosts_from_urls(("https://www.Phishing.test/a", "javascript:alert(1)")) == (
        "phishing.test",
    )
