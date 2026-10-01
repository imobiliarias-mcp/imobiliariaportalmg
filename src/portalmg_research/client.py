"""Central rental research MCP interface and client for Portal Imóveis MG."""

from typing import Optional
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import PortalMGMcpAdapter
from scripts.providers.portalmg import PortalMGRentalProvider


class PortalMGRentalClient:
    """Central rental research client serving as the project's MCP boundary interface."""

    def __init__(
        self,
        provider: Optional[PortalMGRentalProvider] = None,
        mcp_adapter: Optional[PortalMGMcpAdapter] = None,
    ) -> None:
        """Initialize client with provider and MCP adapter."""
        self._provider = provider or PortalMGRentalProvider.create_default()
        self._adapter = mcp_adapter or PortalMGMcpAdapter(provider=self._provider)

    @property
    def mcp_adapter(self) -> PortalMGMcpAdapter:
        """Return the underlying MCP tool adapter."""
        return self._adapter

    def search(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Execute rental search query using domain criteria."""
        return self._provider.search_rentals(search_filter)

    def search_rentals(
        self,
        city_id: str = "2371",
        neighborhood: str = "",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        page: int = 1,
    ) -> RentalSearchResult:
        """Convenience method for searching rental listings."""
        filter_criteria = RentalFilter().with_transaction("locacao").with_page(page)
        if city_id:
            filter_criteria = filter_criteria.with_city(city_id)
        if neighborhood:
            filter_criteria = filter_criteria.with_neighborhood(neighborhood)
        if bedrooms > 0:
            filter_criteria = filter_criteria.with_bedrooms(bedrooms)
        if min_price > 0.0 or max_price > 0.0:
            filter_criteria = filter_criteria.with_price_range(min_price, max_price)
        return self.search(filter_criteria)

    def get_details(self, property_id: str) -> RentalPropertyDetail:
        """Retrieve full details for a specific property listing."""
        code = PropertyCode(property_id)
        return self._provider.get_property_detail(code)

    def get_facets(self) -> FacetCollection:
        """Retrieve taxonomy facets including cities, neighborhoods, and categories."""
        return self._provider.get_facets()
