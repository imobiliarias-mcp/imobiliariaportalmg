"""Domain models, value objects, entities, and criteria for Portal Imóveis MG."""

from scripts.domain.exceptions import (
    PortalMGException,
    PropertyNotFoundException,
    NetworkTransportException,
    ParsingException,
    ValidationException,
)
from scripts.domain.value_objects import (
    PropertyCode,
    ListingPrice,
    RoomCount,
    PageOffset,
    PriceRange,
)
from scripts.domain.entities import (
    RentalPropertySummary,
    RentalPropertyDetail,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingFinancials,
    ListingCore,
    ListingDetails,
    DetailedProfile,
)
from scripts.domain.collections import (
    RentalSearchResult,
    FacetCollection,
    CityItem,
    NeighborhoodItem,
    CategoryItem,
)
from scripts.domain.criteria import (
    RentalFilter,
    LocationFilter,
    PropertyFilter,
    ScopeCriteria,
    ConstraintCriteria,
)

__all__ = [
    "PortalMGException",
    "PropertyNotFoundException",
    "NetworkTransportException",
    "ParsingException",
    "ValidationException",
    "PropertyCode",
    "ListingPrice",
    "RoomCount",
    "PageOffset",
    "PriceRange",
    "RentalPropertySummary",
    "RentalPropertyDetail",
    "ListingIdentity",
    "ListingLocation",
    "ListingSpecs",
    "ListingFinancials",
    "ListingCore",
    "ListingDetails",
    "DetailedProfile",
    "RentalSearchResult",
    "FacetCollection",
    "CityItem",
    "NeighborhoodItem",
    "CategoryItem",
    "RentalFilter",
    "LocationFilter",
    "PropertyFilter",
    "ScopeCriteria",
    "ConstraintCriteria",
]
