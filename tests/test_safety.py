import pytest

from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.external import (
    ExternalStatus,
    ExternalVerdict,
    verdict_from_virustotal,
    virustotal_url_id,
)
from safe_bot.safety.gate import HashError, SafetyGate
from safe_bot.safety.models import Decision, Reason, Submission
from safe_bot.safety.notice import deletion_notice
from safe_bot.safety.urls import extract_urls


class ScriptedChecker:
    def __init__(
        self,
        url_status: ExternalStatus = ExternalStatus.CLEAN,
        file_status: ExternalStatus = ExternalStatus.CLEAN,
    ) -> None:
        self.urls: list[str] = []
        self.files: list[str] = []
        self.url_status = url_status
        self.file_status = file_status

    async def check_url(self, url: str) -> ExternalVerdict:
        self.urls.append(url)
        return ExternalVerdict(self.url_status)

    async def check_file_hash(self, sha256: str) -> ExternalVerdict:
        self.files.append(sha256)
        return ExternalVerdict(self.file_status)


def codes(decision) -> set[str]:
    return {reason.code for reason in decision.reasons}


def test_blocklist_parses_domains_urls_and_hashes() -> None:
    parsed = Blocklist.parse(
        """
        # izoh
        Phishing.Test
        https://www.nested.bad.example/path
        sha256:AA
        sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
        """
    )

    assert parsed.blocks_domain("phishing.test")
    assert parsed.blocks_domain("a.phishing.test")
    assert parsed.blocks_domain("nested.bad.example")
    assert not parsed.blocks_domain("notphishing.test")
    assert "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" in parsed.sha256


def test_extract_urls_finds_plain_links_and_strips_punctuation() -> None:
    assert extract_urls("qara https://evil.test/app.apk.") == ("https://evil.test/app.apk",)


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("https://phishing.test/login", "blocked_domain"),
        ("http://203.0.113.10/get", "ip_host"),
        ("https://user:secret@example.com", "url_userinfo"),
        ("https://files.example/setup.apk", "app_url"),
        ("javascript:alert(1)", "unsafe_scheme"),
    ],
)
async def test_rule_deletes_dangerous_url(url: str, code: str) -> None:
    checker = ScriptedChecker()
    gate = SafetyGate(Blocklist.parse("phishing.test\n"), checker)

    decision = await gate.evaluate(Submission(urls=(url,)))

    assert decision.delete
    assert code in codes(decision)
    assert checker.urls == []


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/news",
        "google.com",
        "www.youtube.com/watch?v=abc",
        "t.me/durov",
        "//example.com/path",
        "tg://resolve?domain=durov",
        "mailto:user@example.com",
        "https://example.com/readme.com",
    ],
)
async def test_ordinary_links_are_allowed(url: str) -> None:
    gate = SafetyGate(Blocklist.parse(""))

    decision = await gate.evaluate(Submission(urls=(url,)))

    assert not decision.delete


async def test_schemeless_blocked_domain_is_still_deleted() -> None:
    gate = SafetyGate(Blocklist.parse("phishing.test"))

    decision = await gate.evaluate(Submission(urls=("phishing.test/login",)))

    assert decision.delete
    assert "blocked_domain" in codes(decision)


async def test_pdf_is_allowed() -> None:
    gate = SafetyGate(Blocklist.parse(""))

    decision = await gate.evaluate(
        Submission(file_name="hisobot.pdf", mime_type="application/pdf")
    )

    assert not decision.delete


async def test_app_file_is_deleted_when_external_checker_is_absent() -> None:
    gate = SafetyGate(Blocklist.parse(""))

    decision = await gate.evaluate(Submission(file_name="app.apk"))

    assert decision.delete
    assert "app_file" in codes(decision)


async def test_android_mime_is_an_app_even_without_extension() -> None:
    gate = SafetyGate(Blocklist.parse(""))

    decision = await gate.evaluate(
        Submission(file_name="file.bin", mime_type="application/vnd.android.package-archive")
    )

    assert "app_file" in codes(decision)


async def test_blocked_hash_is_deleted() -> None:
    digest = "ab" * 32
    gate = SafetyGate(Blocklist.parse(f"sha256:{digest}"))

    decision = await gate.evaluate(Submission(file_name="note.txt", sha256=digest))

    assert decision.delete
    assert "blocked_hash" in codes(decision)


async def test_clean_app_is_allowed_when_virustotal_says_clean() -> None:
    checker = ScriptedChecker(file_status=ExternalStatus.CLEAN)
    gate = SafetyGate(Blocklist.parse(""), checker)

    async def file_hash() -> str:
        return "cd" * 32

    decision = await gate.evaluate(Submission(file_name="app.apk"), file_hash=file_hash)

    assert not decision.delete
    assert checker.files == ["cd" * 32]


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (ExternalStatus.MALICIOUS, "external_malicious_file"),
        (ExternalStatus.UNKNOWN, "external_unknown_file"),
        (ExternalStatus.ERROR, "external_error_file"),
    ],
)
async def test_app_file_is_deleted_when_external_check_is_not_clean(
    status: ExternalStatus, code: str
) -> None:
    gate = SafetyGate(Blocklist.parse(""), ScriptedChecker(file_status=status))

    async def file_hash() -> str:
        return "ef" * 32

    decision = await gate.evaluate(Submission(file_name="run.exe"), file_hash=file_hash)

    assert decision.delete
    assert code in codes(decision)


async def test_external_malicious_url_is_deleted() -> None:
    checker = ScriptedChecker(url_status=ExternalStatus.MALICIOUS)
    gate = SafetyGate(Blocklist.parse(""), checker)

    decision = await gate.evaluate(Submission(urls=("https://example.com",)))

    assert decision.delete
    assert "external_malicious_url" in codes(decision)
    assert checker.urls == ["https://example.com"]


async def test_external_url_error_does_not_delete_ordinary_link() -> None:
    gate = SafetyGate(Blocklist.parse(""), ScriptedChecker(url_status=ExternalStatus.ERROR))

    decision = await gate.evaluate(Submission(urls=("https://example.com",)))

    assert not decision.delete


async def test_hash_provider_error_deletes_app() -> None:
    gate = SafetyGate(Blocklist.parse(""), ScriptedChecker())

    async def file_hash() -> str:
        raise HashError("file_too_large")

    decision = await gate.evaluate(Submission(file_name="app.apk"), file_hash=file_hash)

    assert decision.delete
    assert codes(decision) == {"file_too_large"}


def test_virustotal_payload_and_url_id() -> None:
    malicious = verdict_from_virustotal(
        {"data": {"attributes": {"last_analysis_stats": {"malicious": 2, "harmless": 10}}}}
    )
    clean = verdict_from_virustotal(
        {"data": {"attributes": {"last_analysis_stats": {"harmless": 40, "undetected": 10}}}}
    )
    unknown = verdict_from_virustotal({"data": {"attributes": {}}})

    assert malicious.status is ExternalStatus.MALICIOUS
    assert clean.status is ExternalStatus.CLEAN
    assert unknown.status is ExternalStatus.UNKNOWN
    assert virustotal_url_id("https://example.com")


def test_deletion_notice_is_not_a_link() -> None:
    text = deletion_notice(
        Decision(delete=True, reasons=(Reason("blocked_domain", "phishing.test"),))
    )

    assert "o'chirildi" in text
    assert "phishing.test" in text
    assert "http" not in text
