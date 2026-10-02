"""Query string and parameter builder for Orangeimob search engine."""

from typing import Dict
from urllib.parse import urlencode
from scripts.client.configuration import PortalMGConfiguration
from scripts.domain.criteria import RentalFilter


class RentalQueryBuilder:
    """Builds query parameters and full URLs from RentalFilter specifications."""

    def __init__(self, configuration: PortalMGConfiguration) -> None:
        """Initialize query builder with configuration."""
        self._config = configuration

    def _build_location_params(self, search_filter: RentalFilter) -> Dict[str, str]:
        """Extract location query parameters."""
        loc = search_filter.scope.location
        return {
            "cidade_id": loc.city_id,
            "bairro": loc.neighborhood,
        }

    def _build_property_params(self, search_filter: RentalFilter) -> Dict[str, str]:
        """Extract property specification parameters."""
        prop = search_filter.scope.properties
        return {
            "tipo": prop.category_id,
            "subtipo": prop.subcategory_id,
            "dormitorios": str(prop.bedrooms) if prop.bedrooms > 0 else "",
            "suites": str(prop.suites) if prop.suites > 0 else "",
            "garagens": str(prop.garages) if prop.garages > 0 else "",
            "ref": prop.reference,
        }

    def _build_constraint_params(self, search_filter: RentalFilter) -> Dict[str, str]:
        """Extract pricing, pagination, and sorting parameters."""
        const = search_filter.constraints
        offset = const.pagination.calculate_offset()
        size = const.pagination.page_size()
        return {
            "neg": const.transaction,
            "valor": const.price_range.format_query_param(),
            "por_pagina": str(size),
            "pagina": str(offset),
            "ordenar": const.sort_order,
            "submit": "",
        }

    def build_query_parameters(self, search_filter: RentalFilter) -> Dict[str, str]:
        """Combine all query parameters into a single dictionary."""
        params = {}
        params.update(self._build_constraint_params(search_filter))
        params.update(self._build_location_params(search_filter))
        params.update(self._build_property_params(search_filter))
        return params

    def public_base_url(self) -> str:
        """Return the configured public base, independent of transport URLs."""
        return self._config.public_base_url

    def build_detail_url(self, property_id: str) -> str:
        """Construct the configured API detail endpoint URL."""
        return self._config.detail_url(property_id)

    def build_search_url(self, search_filter: RentalFilter) -> str:
        """Construct full search endpoint URL with encoded parameters."""
        params = self.build_query_parameters(search_filter)
        query_string = urlencode(params)
        base = self._config.search_url()
        return f"{base}?{query_string}"
