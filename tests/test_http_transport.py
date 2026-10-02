"""Regression tests for HTTP failures reaching the transport boundary."""

import httpx
import pytest

from scripts.client.http_transport import PortalMGHttpTransport
from scripts.domain.exceptions import NetworkTransportException

REQUEST_URL = "https://example.test/imoveis_listagem.php"
OPERATIONS = ("get_response", "get_text", "post_form")


def execute_request(transport, operation):
    """Call a transport operation with public query parameters."""
    return getattr(transport, operation)(REQUEST_URL, {"neg": "locacao"})


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("status_code", (404, 500))
def test_http_errors_raise_transport_exception(operation, status_code):
    """Error responses must never be parsed as successful empty results."""
    adapter = httpx.MockTransport(lambda request: httpx.Response(status_code, text="Unavailable"))
    with httpx.Client(transport=adapter) as client:
        transport = PortalMGHttpTransport(http_client=client)
        with pytest.raises(NetworkTransportException) as caught:
            execute_request(transport, operation)
    assert isinstance(caught.value.__cause__, httpx.HTTPStatusError)
    assert str(status_code) in str(caught.value)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_successful_response_preserves_body(operation):
    """Successful requests keep the response body and full-response contract."""
    adapter = httpx.MockTransport(lambda request: httpx.Response(200, text="Rental listings"))
    with httpx.Client(transport=adapter) as client:
        transport = PortalMGHttpTransport(http_client=client)
        result = execute_request(transport, operation)
    if isinstance(result, httpx.Response):
        result = result.text
    assert result == "Rental listings"


def raise_timeout(request):
    """Simulate a network timeout at the HTTP client boundary."""
    raise httpx.ReadTimeout("Request timed out", request=request)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_timeouts_preserve_transport_exception_cause(operation):
    """Network timeouts retain the original specific exception as their cause."""
    with httpx.Client(transport=httpx.MockTransport(raise_timeout)) as client:
        transport = PortalMGHttpTransport(http_client=client)
        with pytest.raises(NetworkTransportException) as caught:
            execute_request(transport, operation)
    assert isinstance(caught.value.__cause__, httpx.ReadTimeout)
