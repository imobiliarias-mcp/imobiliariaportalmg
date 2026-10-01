"""Unit tests for PortalMGRentalProvider with stubbed transport."""

from scripts.client.configuration import PortalMGConfiguration
from scripts.client.http_transport import HttpTransportProtocol
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.providers.portalmg import PortalMGRentalProvider
from tests.test_parsers import SAMPLE_DETAIL_HTML, SAMPLE_SEARCH_HTML


class StubHttpTransport(HttpTransportProtocol):
    """Stub implementation of HttpTransportProtocol returning fixture responses."""

    def get_text(self, url: str, params=None) -> str:
        if "imoveis_detalhes.php" in url:
            return SAMPLE_DETAIL_HTML
        if "imoveis_listagem.php" in url:
            return SAMPLE_SEARCH_HTML
        return ""

    def post_form(self, url: str, data: dict) -> str:
        if "get_bairros_json" in url:
            return '[{"label": "Centro", "value": "Centro"}]'
        if "get_subtipos_json" in url:
            return '[{"label": "Padrão", "value": "8"}]'
        return "[]"


def test_provider_search():
    """Test provider search execution."""
    config = PortalMGConfiguration()
    transport = StubHttpTransport()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)

    res = provider.search_rentals(RentalFilter())
    assert res.total_count() == 2
    assert len(res) == 1
    assert list(res)[0].ref() == "608"


def test_provider_detail():
    """Test provider property detail retrieval."""
    config = PortalMGConfiguration()
    transport = StubHttpTransport()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)

    detail = provider.get_property_detail(PropertyCode("608"))
    assert detail.id() == "608"
    assert detail.summary.price().amount() == 1980.0


def test_provider_facets():
    """Test provider facet retrieval."""
    config = PortalMGConfiguration()
    transport = StubHttpTransport()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)

    facets = provider.get_facets()
    assert len(facets.neighborhoods()) == 1
    assert facets.neighborhoods()[0].name == "Centro"
