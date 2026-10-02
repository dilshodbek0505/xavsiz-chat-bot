import ipaddress
from urllib.parse import unquote, urlsplit

from safe_bot.safety.blocklist import Blocklist
from safe_bot.safety.models import Reason, Submission
from safe_bot.safety.urls import canonical_url

APP_EXTENSIONS = frozenset(
    {
        "apk",
        "apks",
        "xapk",
        "aab",
        "apex",
        "exe",
        "msi",
        "bat",
        "cmd",
        "scr",
        "dll",
        "dex",
        "jar",
    }
)

APP_MIME_TYPES = frozenset(
    {
        "application/vnd.android.package-archive",
        "application/x-android-package-archive",
        "application/x-msdownload",
        "application/x-msdos-program",
        "application/x-msi",
        "application/x-executable",
        "application/x-dosexec",
        "application/java-archive",
        "application/x-dex",
        "application/vnd.microsoft.portable-executable",
    }
)

_SAFE_SCHEMES = frozenset({"http", "https"})
_DANGEROUS_SCHEMES = frozenset(
    {"javascript", "data", "file", "intent", "vbscript", "content"}
)


def is_app_file(submission: Submission) -> bool:
    mime = (submission.mime_type or "").lower()
    if mime in APP_MIME_TYPES:
        return True
    return extension_of(submission.file_name or "") in APP_EXTENSIONS


def extension_of(name: str) -> str | None:
    base = unquote(name).rsplit("/", 1)[-1].split("?", 1)[0].split("#", 1)[0]
    if "." not in base:
        return None
    extension = base.rsplit(".", 1)[-1].lower()
    return extension or None


def rule_reasons(submission: Submission, blocklist: Blocklist) -> tuple[Reason, ...]:
    reasons: list[Reason] = []
    digest = (submission.sha256 or "").lower()
    if digest and digest in blocklist.sha256:
        reasons.append(Reason("blocked_hash"))
    for url in submission.urls:
        reasons.extend(url_reasons(url, blocklist))
    return tuple(reasons)


def url_reasons(url: str, blocklist: Blocklist) -> tuple[Reason, ...]:
    normalized = canonical_url(url)
    if normalized is None:
        return ()
    parts = urlsplit(normalized)
    scheme = parts.scheme.lower()
    if scheme in _DANGEROUS_SCHEMES:
        return (Reason("unsafe_scheme", scheme),)
    if scheme not in _SAFE_SCHEMES:
        return ()

    reasons: list[Reason] = []
    if parts.username or parts.password:
        reasons.append(Reason("url_userinfo"))

    host = (parts.hostname or "").lower().rstrip(".")
    if host and _is_ip(host):
        reasons.append(Reason("ip_host", host))
    elif host and blocklist.blocks_domain(host):
        reasons.append(Reason("blocked_domain", host.removeprefix("www.")))

    extension = extension_of(parts.path)
    if extension in APP_EXTENSIONS:
        reasons.append(Reason("app_url", extension))
    return tuple(reasons)


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True
