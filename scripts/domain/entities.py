"""Domain entities for Portal Imóveis MG rental listings."""

from dataclasses import dataclass
from typing import List, Optional
from scripts.domain.value_objects import ListingPrice, PropertyCode


@dataclass(frozen=True)
class ListingIdentity:
    """Identification codes for a property listing."""

    property_id: str
    reference: PropertyCode

    def code_str(self) -> str:
        """Return reference string."""
        return self.reference.value()


@dataclass(frozen=True)
class ListingLocation:
    """Geographic placement of a property."""

    neighborhood: str
    city: str
    state: str = "MG"
    street: str = ""

    def summary(self) -> str:
        """Return formatted location string."""
        return f"{self.neighborhood}, {self.city} - {self.state}"


@dataclass(frozen=True)
class ListingSpecs:
    """Architectural specifications of a property."""

    bedrooms: int
    bathrooms: int
    suites: int = 0
    garages: int = 0
    area_text: str = ""


@dataclass(frozen=True)
class ListingFinancials:
    """Financial charges associated with a rental property."""

    rental_price: ListingPrice
    condo_fee: Optional[ListingPrice] = None
    iptu: Optional[ListingPrice] = None


@dataclass(frozen=True)
class ListingCore:
    """Core identification and financial values."""

    identity: ListingIdentity
    financials: ListingFinancials


@dataclass(frozen=True)
class ListingDetails:
    """Supplementary descriptive attributes."""

    location: ListingLocation
    category: str
    thumbnail_url: str = ""
    detail_url: str = ""


@dataclass(frozen=True)
class RentalPropertySummary:
    """Summary entity representing a search result listing card."""

    core: ListingCore
    details: ListingDetails

    def id(self) -> str:
        """Return property ID."""
        return self.core.identity.property_id

    def ref(self) -> str:
        """Return reference code."""
        return self.core.identity.code_str()

    def price(self) -> ListingPrice:
        """Return rental price."""
        return self.core.financials.rental_price

    def to_dictionary(self) -> dict:
        """Convert summary into dictionary for MCP tools."""
        return {
            "property_id": self.core.identity.property_id,
            "reference": self.core.identity.code_str(),
            "category": self.details.category,
            "neighborhood": self.details.location.neighborhood,
            "city": self.details.location.city,
            "state": self.details.location.state,
            "rental_price": self.core.financials.rental_price.amount(),
            "rental_price_formatted": self.core.financials.rental_price.format_brl(),
            "thumbnail_url": self.details.thumbnail_url,
            "detail_url": self.details.detail_url,
        }


@dataclass(frozen=True)
class DetailedProfile:
    """Extended specifications, amenities, and photo assets."""

    specs: ListingSpecs
    amenities: List[str]
    photos: List[str]
    map_url: str = ""


@dataclass(frozen=True)
class RentalPropertyDetail:
    """Complete detail entity for a rental property listing."""

    summary: RentalPropertySummary
    profile: DetailedProfile

    def id(self) -> str:
        """Return property ID."""
        return self.summary.id()

    def ref(self) -> str:
        """Return reference code."""
        return self.summary.ref()

    def to_dictionary(self) -> dict:
        """Convert complete detail into dictionary for MCP tools."""
        data = self.summary.to_dictionary()
        data["bedrooms"] = self.profile.specs.bedrooms
        data["bathrooms"] = self.profile.specs.bathrooms
        data["suites"] = self.profile.specs.suites
        data["garages"] = self.profile.specs.garages
        data["area"] = self.profile.specs.area_text
        data["amenities"] = list(self.profile.amenities)
        data["photos"] = list(self.profile.photos)
        data["map_url"] = self.profile.map_url
        data["condo_fee"] = (
            self.summary.core.financials.condo_fee.format_brl()
            if self.summary.core.financials.condo_fee
            else None
        )
        return data
