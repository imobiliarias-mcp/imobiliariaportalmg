"""Unit tests for PortalMGMcpAdapter."""

from scripts.client.configuration import PortalMGConfiguration
from scripts.client.query_builder import RentalQueryBuilder
from scripts.mcp.tools import PortalMGMcpAdapter
from scripts.providers.portalmg import PortalMGRentalProvider
from tests.test_provider import StubHttpTransport


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    transport = StubHttpTransport()
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)
    adapter = PortalMGMcpAdapter(provider=provider)

    info = adapter.get_provider_info()
    assert info["provider_name"] == "portalmg"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    transport = StubHttpTransport()
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)
    adapter = PortalMGMcpAdapter(provider=provider)

    result_dict = adapter.search_rentals(city_id="2371", bedrooms=2, max_price=2000.0)
    assert isinstance(result_dict, dict)
    assert result_dict["total_count"] == 2
    assert len(result_dict["listings"]) == 1
    assert result_dict["listings"][0]["reference"] == "608"


def test_mcp_adapter_property_detail():
    """Test MCP detail tool execution."""
    transport = StubHttpTransport()
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)
    adapter = PortalMGMcpAdapter(provider=provider)

    detail_dict = adapter.get_property_detail("608")
    assert isinstance(detail_dict, dict)
    assert detail_dict["reference"] == "608"
    assert detail_dict["rental_price"] == 1980.0
    assert detail_dict["bedrooms"] == 3


def test_mcp_adapter_facets():
    """Test MCP facets tool execution."""
    transport = StubHttpTransport()
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)
    adapter = PortalMGMcpAdapter(provider=provider)

    facets_dict = adapter.get_facets()
    assert isinstance(facets_dict, dict)
    assert "neighborhoods" in facets_dict
    assert len(facets_dict["neighborhoods"]) == 1
