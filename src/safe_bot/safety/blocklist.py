from pathlib import Path
from urllib.parse import urlsplit


class Blocklist:
    def __init__(self, domains: frozenset[str], sha256: frozenset[str]) -> None:
        self.domains = domains
        self.sha256 = sha256

    @classmethod
    def parse(cls, text: str) -> "Blocklist":
        domains: set[str] = set()
        hashes: set[str] = set()
        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip().lower()
            if not line:
                continue
            if line.startswith("sha256:"):
                digest = line.removeprefix("sha256:").strip()
                if _is_sha256(digest):
                    hashes.add(digest)
                continue
            host = _host_from_entry(line)
            if host and "." in host:
                domains.add(host)
        return cls(frozenset(domains), frozenset(hashes))

    @classmethod
    def load(cls, path: Path) -> "Blocklist":
        if not path.is_file():
            return cls.parse("")
        return cls.parse(path.read_text(encoding="utf-8"))

    def blocks_domain(self, host: str) -> bool:
        normalized = host.lower().rstrip(".").removeprefix("www.")
        labels = normalized.split(".")
        for index in range(len(labels)):
            candidate = ".".join(labels[index:])
            if "." in candidate and candidate in self.domains:
                return True
        return False


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _host_from_entry(line: str) -> str | None:
    if "://" in line:
        host = urlsplit(line).hostname
    else:
        host = line.split("/", 1)[0].split(":", 1)[0]
    if not host:
        return None
    return host.lower().rstrip(".").removeprefix("www.")
