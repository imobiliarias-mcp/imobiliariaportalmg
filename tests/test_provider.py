"""Unit tests for PortalMGRentalProvider with stubbed transport."""

from scripts.client.configuration import PortalMGConfiguration
from scripts.client.http_transport import HttpTransportProtocol
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.providers.portalmg import PortalMGRentalProvider
from scripts.run_search import display_results
from scripts.verify_research import test_rental_search as verify_rental_search
from tests.test_parsers import SAMPLE_DETAIL_HTML, SAMPLE_SEARCH_HTML


class StubHttpTransport(HttpTransportProtocol):
    """Stub implementation of HttpTransportProtocol returning fixture responses."""

    def __init__(self) -> None:
        self.requested_urls = []

    def get_text(self, url: str, params=None) -> str:
        self.requested_urls.append(url)
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


def test_provider_detail_serializes_configured_public_url_without_using_transport_host():
    config = PortalMGConfiguration(
        base_url="https://api.example",
        public_base_url="https://public.example",
    )
    transport = StubHttpTransport()
    provider = PortalMGRentalProvider(
        transport=transport,
        query_builder=RentalQueryBuilder(config),
    )

    detail = provider.get_property_detail(PropertyCode("608"))

    assert detail.summary.to_dictionary()["url"] == (
        "https://public.example/imoveis_detalhes.php?id=608"
    )
    assert detail.summary.details.detail_url == "imoveis_detalhes.php?id=608"
    assert transport.requested_urls == ["https://api.example/imoveis_detalhes.php?id=608"]


def test_provider_facets():
    """Test provider facet retrieval."""
    config = PortalMGConfiguration()
    transport = StubHttpTransport()
    builder = RentalQueryBuilder(config)
    provider = PortalMGRentalProvider(transport=transport, query_builder=builder)

    facets = provider.get_facets()
    assert len(facets.neighborhoods()) == 1
    assert facets.neighborhoods()[0].name == "Centro"


def test_provider_forwards_public_base_without_detail_requests():
    config = PortalMGConfiguration(
        base_url="https://api.example",
        public_base_url="https://public.example",
    )
    transport = StubHttpTransport()
    provider = PortalMGRentalProvider(
        transport=transport,
        query_builder=RentalQueryBuilder(config),
    )

    result = provider.search_rentals(RentalFilter())
    listing = next(iter(result))
    assert listing.details.url == "https://public.example/imoveis_detalhes.php?id=608"
    assert listing.details.detail_url == "imoveis_detalhes.php?id=608"
    assert len(transport.requested_urls) == 1
    assert transport.requested_urls[0].startswith("https://api.example/")


def _stubbed_search_result():
    configuration = PortalMGConfiguration()
    transport = StubHttpTransport()
    provider = PortalMGRentalProvider(
        transport=transport,
        query_builder=RentalQueryBuilder(configuration),
    )
    return provider.search_rentals(RentalFilter())


def test_search_cli_prints_public_link(capsys):
    display_results(_stubbed_search_result())
    assert "Link: https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608" in capsys.readouterr().out


def test_verification_runner_prints_public_link(capsys):
    class StubClient:
        def search_rentals(self, city_id):
            return _stubbed_search_result()

    verify_rental_search(StubClient())
    assert "Link: https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608" in capsys.readouterr().out
