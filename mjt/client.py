import asyncio
import logging
import re
import time
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://mjt.trans.my.id"
WEB_URL = f"{BASE_URL}/pis/web"
BUSES_URL = f"{BASE_URL}/pis/ajax/json_getInitialBuses"
ROUTES_URL = f"{BASE_URL}/pis/ajax/json_getRoutes"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class MJTClient:
    """Async Client for interacting with the MJT (Trans) service."""

    def __init__(self, token_ttl_seconds: int = 300, timeout: float = 15.0):
        self.token_ttl_seconds = token_ttl_seconds
        self.timeout = timeout
        self._lock = asyncio.Lock()
        self._pis_nonce: Optional[str] = None
        self._mjt_cookie: Optional[str] = None
        self._xtoken_cookie: Optional[str] = None
        self._tokens_updated_at: float = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=DEFAULT_HEADERS,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def is_token_expired(self) -> bool:
        if not self._pis_nonce or not self._mjt_cookie:
            return True
        return (time.time() - self._tokens_updated_at) >= self.token_ttl_seconds

    def get_remaining_ttl(self) -> int:
        if not self._tokens_updated_at:
            return 0
        remaining = int(self.token_ttl_seconds - (time.time() - self._tokens_updated_at))
        return max(0, remaining)

    async def get_tokens(self, force: bool = False) -> Dict[str, Any]:
        """Returns cached tokens if within TTL (300s), otherwise fetches fresh tokens."""
        if not force and not self.is_token_expired():
            return {
                "pis_nonce": self._pis_nonce,
                "mjt_cookie": self._mjt_cookie,
                "xtoken_cookie": self._xtoken_cookie,
                "expires_in": self.get_remaining_ttl(),
                "cached": True,
            }
        return await self.refresh_tokens(force=True)

    async def refresh_tokens(self, force: bool = False) -> Dict[str, Any]:
        async with self._lock:
            if not force and not self.is_token_expired():
                return {
                    "pis_nonce": self._pis_nonce,
                    "mjt_cookie": self._mjt_cookie,
                    "xtoken_cookie": self._xtoken_cookie,
                    "expires_in": self.get_remaining_ttl(),
                    "cached": True,
                }

            logger.info("Fetching fresh session tokens from MJT web...")
            client = await self.get_client()
            client.cookies.clear()

            response = await client.get(WEB_URL)
            response.raise_for_status()

            match = re.search(r"pisNonce:\s*'([^']+)'", response.text)
            pis_nonce = match.group(1) if match else None

            # Extract dynamic TTL if provided by upstream (e.g. pisNonceTtl: 300)
            ttl_match = re.search(r"pisNonceTtl:\s*(\d+)", response.text)
            if ttl_match:
                self.token_ttl_seconds = int(ttl_match.group(1))

            # Extract cookies from response or client jar
            mjt_cookie = response.cookies.get("mjt") or client.cookies.get("mjt")
            xtoken_cookie = (
                response.cookies.get("X-TOKEN")
                or response.cookies.get("X-token")
                or client.cookies.get("X-TOKEN")
                or client.cookies.get("X-token")
            )

            if not pis_nonce:
                logger.warning("pisNonce not found in response HTML.")

            self._pis_nonce = pis_nonce
            self._mjt_cookie = mjt_cookie
            self._xtoken_cookie = xtoken_cookie
            self._tokens_updated_at = time.time()

            return {
                "pis_nonce": self._pis_nonce,
                "mjt_cookie": self._mjt_cookie,
                "xtoken_cookie": self._xtoken_cookie,
                "expires_in": self.token_ttl_seconds,
                "cached": False,
            }

    async def _get_ajax_headers(self) -> Dict[str, str]:
        if self.is_token_expired():
            await self.refresh_tokens()

        cookie_str = f"mjt={self._mjt_cookie or ''}; X-token={self._xtoken_cookie or ''}"
        return {
            "Cookie": cookie_str,
            "Origin": WEB_URL,
            "Referer": WEB_URL,
            "X-Pis-Nonce": self._pis_nonce or "",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

    async def _fetch_ajax(self, url: str) -> Any:
        client = await self.get_client()
        headers = await self._get_ajax_headers()

        res = await client.get(url, headers=headers)

        # If unauthorized or forbidden or nonce rejected, try refreshing tokens once
        if res.status_code in (401, 403) or "pisNonce" in res.text:
            logger.info("Session may have expired, refreshing tokens and retrying...")
            await self.refresh_tokens(force=True)
            headers = await self._get_ajax_headers()
            res = await client.get(url, headers=headers)

        res.raise_for_status()
        return res.json()

    async def get_initial_buses(self) -> Any:
        return await self._fetch_ajax(BUSES_URL)

    async def get_routes(self) -> Any:
        return await self._fetch_ajax(ROUTES_URL)


# Singleton client instance for MJT
mjt_client = MJTClient()
