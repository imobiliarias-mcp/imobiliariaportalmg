"""HTTP transport layer for communicating with Portal Imóveis MG."""

from typing import Dict, Optional, Protocol
import httpx
from scripts.client.configuration import PortalMGConfiguration
from scripts.domain.exceptions import NetworkTransportException


class HttpTransportProtocol(Protocol):
    """Protocol for HTTP communication mechanisms."""

    def get_text(self, url: str, params: Optional[Dict[str, str]] = None) -> str:
        """Execute GET request and return response text."""
        ...

    def post_form(self, url: str, data: Dict[str, str]) -> str:
        """Execute POST form request and return response text."""
        ...


class PortalMGHttpTransport(HttpTransportProtocol):
    """Concrete HTTP transport using httpx."""

    def __init__(
        self,
        configuration: Optional[PortalMGConfiguration] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize transport with config and client."""
        self._config = configuration or PortalMGConfiguration()
        self._client = http_client or httpx.Client(
            timeout=self._config.timeout_seconds,
            follow_redirects=True,
        )

    def _default_headers(self) -> Dict[str, str]:
        """Construct standard browser headers."""
        return {
            "User-Agent": self._config.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def get_text(self, url: str, params: Optional[Dict[str, str]] = None) -> str:
        """Execute GET request and return body text."""
        resp = self.get_response(url, params)
        return resp.text

    def get_response(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Execute GET request returning full HTTP response."""
        try:
            headers = self._default_headers()
            return self._client.get(url, params=params, headers=headers)
        except Exception as exc:
            raise NetworkTransportException(f"GET request failed for {url}: {exc}") from exc

    def post_form(self, url: str, data: Dict[str, str]) -> str:
        """Execute POST form request and return response body text."""
        try:
            headers = self._default_headers()
            headers["X-Requested-With"] = "XMLHttpRequest"
            resp = self._client.post(url, data=data, headers=headers)
            return resp.text
        except Exception as exc:
            raise NetworkTransportException(f"POST request failed for {url}: {exc}") from exc
