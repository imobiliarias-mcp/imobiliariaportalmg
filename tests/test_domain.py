"""Unit tests for domain value objects, entities, criteria, and collections."""

import pytest
from scripts.domain.collections import (
    CityItem,
    FacetCollection,
    NeighborhoodItem,
    RentalSearchResult,
)
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import (
    ListingCore,
    ListingDetails,
    ListingFinancials,
    ListingIdentity,
    ListingLocation,
    RentalPropertySummary,
)
from scripts.domain.exceptions import ValidationException
from scripts.domain.value_objects import (
    ListingPrice,
    PageOffset,
    PriceRange,
    PropertyCode,
    RoomCount,
)


def test_property_code_valid():
    """Test valid property code."""
    code = PropertyCode("608")
    assert code.value() == "608"
    assert str(code) == "608"


def test_property_code_empty_raises_validation():
    """Test empty property code raises error."""
    with pytest.raises(ValidationException):
        PropertyCode("   ")


def test_listing_price_format():
    """Test BRL price formatting."""
    price = ListingPrice(1980.50)
    assert price.amount() == 1980.50
    assert price.format_brl() == "R$ 1.980,50"


def test_listing_price_negative_raises_validation():
    """Test negative price raises error."""
    with pytest.raises(ValidationException):
        ListingPrice(-10.0)


def test_room_count_valid():
    """Test room count validation."""
    rooms = RoomCount(3)
    assert rooms.count() == 3


def test_room_count_negative_raises_validation():
    """Test negative room count raises error."""
    with pytest.raises(ValidationException):
        RoomCount(-1)


def test_page_offset_calculation():
    """Test offset calculation formula."""
    p1 = PageOffset(page=1, page_size=10)
    assert p1.calculate_offset() == 0

    p2 = PageOffset(page=2, page_size=10)
    assert p2.calculate_offset() == 10

    p3_size30 = PageOffset(page=3, page_size=30)
    assert p3_size30.calculate_offset() == 60


def test_page_offset_invalid():
    """Test invalid page number and page size."""
    with pytest.raises(ValidationException):
        PageOffset(page=0)
    with pytest.raises(ValidationException):
        PageOffset(page=1, page_size=15)


def test_price_range_formatting():
    """Test bounded and unbounded price range query formatting."""
    bounded = PriceRange(minimum=500.0, maximum=1500.0)
    assert bounded.format_query_param() == "500-1500.00"

    unbounded = PriceRange(minimum=2000.0, maximum=0.0)
    assert unbounded.is_unbounded() is True
    assert unbounded.format_query_param() == "2000-i"

    empty = PriceRange(minimum=0.0, maximum=0.0)
    assert empty.format_query_param() == ""


def test_price_range_invalid_inversion():
    """Test inverted price range raises error."""
    with pytest.raises(ValidationException):
        PriceRange(minimum=2000.0, maximum=1000.0)


def test_rental_filter_immutable_builder():
    """Test fluent immutable RentalFilter modifications."""
    f1 = RentalFilter()
    assert f1.constraints.transaction == "locacao"

    f2 = f1.with_city("2371").with_neighborhood("Centro").with_bedrooms(2)
    assert f2.scope.location.city_id == "2371"
    assert f2.scope.location.neighborhood == "Centro"
    assert f2.scope.properties.bedrooms == 2
    # Ensure immutability of original
    assert f1.scope.location.city_id == ""
    assert f1.scope.properties.bedrooms == 0


def test_rental_search_result_pagination_math():
    """Test total pages and pagination logic."""
    core = ListingCore(
        identity=ListingIdentity("1", PropertyCode("1")),
        financials=ListingFinancials(ListingPrice(1000.0)),
    )
    details = ListingDetails(ListingLocation("Centro", "Timóteo"), "Casas")
    summary = RentalPropertySummary(core=core, details=details)

    res = RentalSearchResult(items=[summary], total_count=25, current_page=1, page_size=10)
    assert res.total_pages() == 3
    assert res.has_next_page() is True
    assert len(res) == 1

    d = res.to_dictionary()
    assert d["total_count"] == 25
    assert d["total_pages"] == 3
    assert len(d["listings"]) == 1


def test_facet_collection_dictionary():
    """Test FacetCollection dictionary serialization."""
    cities = [CityItem(city_id="2371", name="Timóteo")]
    neighborhoods = [NeighborhoodItem(name="Centro", city_id="2371")]
    facets = FacetCollection(cities=cities, neighborhoods=neighborhoods, categories=[])
    d = facets.to_dictionary()
    assert len(d["cities"]) == 1
    assert d["cities"][0]["id"] == "2371"
    assert len(d["neighborhoods"]) == 1
