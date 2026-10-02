import base64
from enum import StrEnum
from typing import Protocol

import aiohttp


class ExternalStatus(StrEnum):
    MALICIOUS = "malicious"
    CLEAN = "clean"
    UNKNOWN = "unknown"
    ERROR = "error"


class ExternalVerdict:
    def __init__(self, status: ExternalStatus, detail: str = "") -> None:
        self.status = status
        self.detail = detail


class ExternalChecker(Protocol):
    async def check_url(self, url: str) -> ExternalVerdict: ...

    async def check_file_hash(self, sha256: str) -> ExternalVerdict: ...


def virustotal_url_id(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


def verdict_from_virustotal(payload: dict) -> ExternalVerdict:
    stats = payload.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    if not isinstance(stats, dict) or not stats:
        return ExternalVerdict(ExternalStatus.UNKNOWN)
    if stats.get("malicious", 0) or stats.get("suspicious", 0):
        return ExternalVerdict(ExternalStatus.MALICIOUS)
    if stats.get("harmless", 0) or stats.get("undetected", 0):
        return ExternalVerdict(ExternalStatus.CLEAN)
    return ExternalVerdict(ExternalStatus.UNKNOWN)


class VirusTotalChecker:
    """Faylni yuklamaydi. Faqat mavjud URL hisoboti va SHA-256 ni so'raydi."""

    def __init__(self, api_key: str, *, timeout: float = 10.0) -> None:
        self._api_key = api_key
        self._timeout = timeout

    async def check_url(self, url: str) -> ExternalVerdict:
        url_id = virustotal_url_id(url)
        return await self._get(f"https://www.virustotal.com/api/v3/urls/{url_id}")

    async def check_file_hash(self, sha256: str) -> ExternalVerdict:
        return await self._get(f"https://www.virustotal.com/api/v3/files/{sha256}")

    async def _get(self, url: str) -> ExternalVerdict:
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers={"x-apikey": self._api_key}) as response:
                    if response.status == 404:
                        return ExternalVerdict(ExternalStatus.UNKNOWN)
                    if response.status != 200:
                        return ExternalVerdict(ExternalStatus.ERROR, detail=str(response.status))
                    payload = await response.json()
        except (aiohttp.ClientError, TimeoutError):
            return ExternalVerdict(ExternalStatus.ERROR, detail="tarmoq xatosi")
        if not isinstance(payload, dict):
            return ExternalVerdict(ExternalStatus.ERROR, detail="javob")
        return verdict_from_virustotal(payload)
