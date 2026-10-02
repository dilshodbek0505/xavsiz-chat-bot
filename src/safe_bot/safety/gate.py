from collections.abc import Awaitable, Callable

from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.external import ExternalChecker, ExternalStatus
from safe_bot.safety.models import Decision, Reason, Submission
from safe_bot.safety.rules import is_app_file, rule_reasons


class HashError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SafetyGate:
    """Avval qoidalar. Ular xavfli desa, tashqi tekshiruv qarorni o'zgartirmaydi."""

    def __init__(self, blocklist: Blocklist, external: ExternalChecker | None = None) -> None:
        self.blocklist = blocklist
        self.external = external

    async def evaluate(
        self,
        submission: Submission,
        *,
        file_hash: Callable[[], Awaitable[str | None]] | None = None,
    ) -> Decision:
        reasons = rule_reasons(submission, self.blocklist)
        if reasons:
            return Decision(True, reasons)

        app = is_app_file(submission)
        if self.external is None:
            if app:
                return Decision(True, (Reason("app_file", submission.file_name or ""),))
            return Decision(False)

        url_hits = await self._malicious_urls(submission.urls)
        if url_hits:
            return Decision(True, tuple(url_hits))
        if not app:
            return Decision(False)

        digest = await self._resolve_hash(submission, file_hash)
        if isinstance(digest, Decision):
            return digest
        if digest in self.blocklist.sha256:
            return Decision(True, (Reason("blocked_hash"),))

        verdict = await self.external.check_file_hash(digest)
        if verdict.status is ExternalStatus.MALICIOUS:
            return Decision(True, (Reason("external_malicious_file"),))
        if verdict.status is ExternalStatus.CLEAN:
            return Decision(False)
        if verdict.status is ExternalStatus.ERROR:
            return Decision(True, (Reason("external_error_file"),))
        return Decision(True, (Reason("external_unknown_file"),))

    async def _malicious_urls(self, urls: tuple[str, ...]) -> list[Reason]:
        if self.external is None:
            return []
        reasons: list[Reason] = []
        for url in urls:
            verdict = await self.external.check_url(url)
            if verdict.status is ExternalStatus.MALICIOUS:
                reasons.append(Reason("external_malicious_url", _public_host(url)))
        return reasons

    async def _resolve_hash(
        self,
        submission: Submission,
        file_hash: Callable[[], Awaitable[str | None]] | None,
    ) -> str | Decision:
        if submission.sha256:
            return submission.sha256.lower()
        if file_hash is None:
            return Decision(True, (Reason("hash_unavailable"),))
        try:
            digest = await file_hash()
        except HashError as exc:
            return Decision(True, (Reason(exc.code),))
        if not digest:
            return Decision(True, (Reason("hash_unavailable"),))
        return digest.lower()


def _public_host(url: str) -> str:
    from urllib.parse import urlsplit

    host = urlsplit(url).hostname
    if not host:
        return "havola"
    return host.removeprefix("www.")
