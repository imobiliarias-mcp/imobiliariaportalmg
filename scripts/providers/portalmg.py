"""Portal Imóveis MG rental search provider implementation."""

from typing import Optional
from scripts.client.configuration import PortalMGConfiguration
from scripts.client.http_transport import PortalMGHttpTransport
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol


class PortalMGRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Portal Imóveis MG."""

    def __init__(
        self,
        transport: PortalMGHttpTransport,
        query_builder: RentalQueryBuilder,
    ) -> None:
        """Initialize provider with transport and query builder."""
        self._transport = transport
        self._builder = query_builder

    @classmethod
    def create_default(
        cls,
        configuration: Optional[PortalMGConfiguration] = None,
    ) -> "PortalMGRentalProvider":
        """Factory method constructing provider with default configurations."""
        config = configuration or PortalMGConfiguration()
        transport = PortalMGHttpTransport(configuration=config)
        builder = RentalQueryBuilder(configuration=config)
        return cls(transport=transport, query_builder=builder)

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "portalmg"

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings using criteria filter."""
        search_url = self._builder.build_search_url(search_filter)
        html_content = self._transport.get_text(search_url)
        parser = SearchResultParser(public_base_url=self._builder.public_base_url())
        page = search_filter.constraints.pagination.page_number()
        size = search_filter.constraints.pagination.page_size()
        return parser.parse_search_response(html_content, current_page=page, page_size=size)

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details for a single property by code."""
        code_str = code.value()
        detail_url = self._builder.build_detail_url(code_str)
        html_content = self._transport.get_text(detail_url)
        parser = PropertyDetailParser(public_base_url=self._builder.public_base_url())
        return parser.parse_detail_response(html_content, property_id=code_str)

    def get_facets(self) -> FacetCollection:
        """Retrieve available cities, neighborhoods, and filter options."""
        search_url = "https://www.imobiliariaportalmg.com.br/imoveis_listagem.php"
        search_html = self._transport.get_text(search_url)
        parser = FacetParser()
        cities = parser.parse_cities_from_html(search_html)
        bairros_json = self._transport.post_form(
            "https://www.imobiliariaportalmg.com.br/ajax.php?function=get_bairros_json",
            data={},
        )
        neighborhoods = parser.parse_neighborhoods(bairros_json)
        subtipos_json = self._transport.post_form(
            "https://www.imobiliariaportalmg.com.br/ajax.php?function=get_subtipos_json",
            data={},
        )
        categories = parser.parse_categories(subtipos_json)
        return FacetCollection(cities=cities, neighborhoods=neighborhoods, categories=categories)
