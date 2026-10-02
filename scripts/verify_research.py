#!/usr/bin/env python3
"""Comprehensive end-to-end verification script for Portal Imóveis MG research."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.criteria import RentalFilter
from scripts.domain.exceptions import PropertyNotFoundException
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import PortalMGMcpAdapter
from scripts.providers.portalmg import PortalMGRentalProvider
from src.portalmg_research.client import PortalMGRentalClient


def test_target_search(client: PortalMGRentalClient) -> None:
    """1. Verify reproduction of prompt target search URL."""
    print("\n--- 1. Target URL Search (neg=&dormitorios=1) ---")
    flt = RentalFilter().with_transaction("").with_bedrooms(1)
    results = client.search(flt)
    print(f"Total matching listings: {results.total_count()} (returned on page 1: {len(results)})")
    assert len(results) > 0, "Target search returned no listings."
    sample = list(results)[0]
    print(f"Sample listing: [{sample.ref()}] {sample.details.category} - {sample.price().format_brl()}")


def test_rental_search(client: PortalMGRentalClient) -> None:
    """2. Verify standard rental listings in Timóteo."""
    print("\n--- 2. Timóteo Rental Listings Search ---")
    results = client.search_rentals(city_id="2371")
    print(f"Total rental listings in Timóteo: {results.total_count()}")
    assert results.total_count() > 0, "No rental listings found for Timóteo."
    for item in list(results)[:3]:
        print(f"  [{item.ref()}] {item.details.category:<12} | {item.details.location.summary():<25} | {item.price().format_brl()}")
        print(f"    Link: {item.details.url}")


def test_filter_combinations(client: PortalMGRentalClient) -> None:
    """3. Verify multi-parameter filter combinations."""
    print("\n--- 3. Filter Combinations ---")
    # A. Neighborhood filter
    flt_bairro = RentalFilter().with_city("2371").with_neighborhood("Centro")
    res_bairro = client.search(flt_bairro)
    print(f"  Rentals in Centro: {res_bairro.total_count()} found")
    assert res_bairro.total_count() > 0, "Expected rentals in Centro"

    # B. Price range filter
    flt_price = RentalFilter().with_price_range(1.0, 1000.0)
    res_price = client.search(flt_price)
    print(f"  Rentals <= R$ 1.000: {res_price.total_count()} found")

    # C. Unbounded price range
    flt_high = RentalFilter().with_price_range(1501.0, 0.0)
    res_high = client.search(flt_high)
    print(f"  Rentals >= R$ 1.501: {res_high.total_count()} found")


def test_pagination_boundary(client: PortalMGRentalClient) -> None:
    """4. Verify pagination mechanics and boundary behavior."""
    print("\n--- 4. Pagination & Boundary Behavior ---")
    # Requesting out-of-bounds offset
    out_of_bounds_filter = RentalFilter().with_page(999)
    res_empty = client.search(out_of_bounds_filter)
    print(f"  Page 999 result count: {len(res_empty)} listings (handled gracefully)")
    assert len(res_empty) == 0, "Out-of-bounds page should return 0 items."


def test_property_details(client: PortalMGRentalClient) -> None:
    """5. Verify property detail retrieval and not-found handling."""
    print("\n--- 5. Property Detail Retrieval ---")
    detail_608 = client.get_details("608")
    print(f"  [REF {detail_608.ref()}] Aluguel: {detail_608.summary.price().format_brl()}")
    print(f"  Amenities count: {len(detail_608.profile.amenities)}")
    print(f"  Photos count: {len(detail_608.profile.photos)}")
    assert len(detail_608.profile.photos) > 0, "Expected photo assets in gallery"

    detail_547 = client.get_details("547")
    print(f"  [REF {detail_547.ref()}] Aluguel: {detail_547.summary.price().format_brl()}")
    print(f"  Specs: {detail_547.profile.specs.bedrooms} quartos, {detail_547.profile.specs.bathrooms} banheiros, Área: {detail_547.profile.specs.area_text}")
    assert detail_547.profile.specs.bedrooms == 1
    assert detail_547.profile.specs.bathrooms == 1

    # Not-found validation
    try:
        client.get_details("999999")
        raise AssertionError("Non-existent property should raise PropertyNotFoundException")
    except PropertyNotFoundException:
        print("  Non-existent property ID 999999 correctly raised PropertyNotFoundException.")


def test_facets_discovery(client: PortalMGRentalClient) -> None:
    """6. Verify AJAX taxonomy facet discovery."""
    print("\n--- 6. AJAX Facet Discovery ---")
    facets = client.get_facets()
    cities = facets.cities()
    neighborhoods = facets.neighborhoods()
    categories = facets.categories()
    print(f"  Cities: {len(cities)} indexed")
    print(f"  Neighborhoods: {len(neighborhoods)} indexed")
    print(f"  Categories: {len(categories)} indexed")
    assert len(cities) > 0, "Expected cities in facet collection"
    assert len(neighborhoods) > 0, "Expected neighborhoods in facet collection"


def test_mcp_adapter() -> None:
    """7. Verify MCP Adapter conforms to tool registry protocol."""
    print("\n--- 7. MCP Adapter Interface Validation ---")
    adapter = PortalMGMcpAdapter.create_default()
    info = adapter.get_provider_info()
    print(f"  Provider Name: {info['provider_name']}")
    assert info["provider_name"] == "portalmg"

    search_dict = adapter.search_rentals(city_id="2371", page=1)
    print(f"  MCP search_rentals returned dict with keys: {list(search_dict.keys())}")
    assert "total_count" in search_dict
    assert "listings" in search_dict

    detail_dict = adapter.get_property_detail("608")
    print(f"  MCP get_property_detail returned dict with reference: {detail_dict.get('reference')}")
    assert detail_dict.get("reference") == "608"


def main() -> None:
    """Run all verification tests."""
    print("=== Starting Portal Imóveis MG Research Verification ===")
    provider = PortalMGRentalProvider.create_default()
    client = PortalMGRentalClient(provider=provider)

    test_target_search(client)
    test_rental_search(client)
    test_filter_combinations(client)
    test_pagination_boundary(client)
    test_property_details(client)
    test_facets_discovery(client)
    test_mcp_adapter()

    print("\n=== All Verification Checks Passed Successfully! ===")


if __name__ == "__main__":
    main()
