"""Portal Imóveis MG Central Rental Research Package."""

from scripts.domain.collections import (
    CategoryItem,
    CityItem,
    FacetCollection,
    NeighborhoodItem,
    RentalSearchResult,
)
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import (
    DetailedProfile,
    RentalPropertyDetail,
    RentalPropertySummary,
)
from scripts.domain.exceptions import (
    NetworkTransportException,
    ParsingException,
    PortalMGException,
    PropertyNotFoundException,
    ValidationException,
)
from scripts.domain.value_objects import (
    ListingPrice,
    PageOffset,
    PriceRange,
    PropertyCode,
    RoomCount,
)
from scripts.mcp.tools import PortalMGMcpAdapter
from scripts.providers.portalmg import PortalMGRentalProvider
from src.portalmg_research.client import PortalMGRentalClient

__all__ = [
    "PortalMGRentalClient",
    "PortalMGRentalProvider",
    "PortalMGMcpAdapter",
    "RentalFilter",
    "PropertyCode",
    "ListingPrice",
    "RoomCount",
    "PageOffset",
    "PriceRange",
    "RentalSearchResult",
    "FacetCollection",
    "CityItem",
    "NeighborhoodItem",
    "CategoryItem",
    "RentalPropertySummary",
    "RentalPropertyDetail",
    "DetailedProfile",
    "PortalMGException",
    "PropertyNotFoundException",
    "NetworkTransportException",
    "ParsingException",
    "ValidationException",
]
