"""Client layer for HTTP communications and document parsing."""

from scripts.client.configuration import PortalMGConfiguration
from scripts.client.http_transport import (
    HttpTransportProtocol,
    PortalMGHttpTransport,
)
from scripts.client.parsers import (
    SearchResultParser,
    PropertyDetailParser,
    FacetParser,
)
from scripts.client.query_builder import RentalQueryBuilder

__all__ = [
    "PortalMGConfiguration",
    "HttpTransportProtocol",
    "PortalMGHttpTransport",
    "SearchResultParser",
    "PropertyDetailParser",
    "FacetParser",
    "RentalQueryBuilder",
]
