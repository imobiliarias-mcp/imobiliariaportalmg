"""Unit tests for Orangeimob search query builder."""

from scripts.client.configuration import PortalMGConfiguration
from scripts.client.query_builder import RentalQueryBuilder
from scripts.domain.criteria import RentalFilter


def test_default_rental_query():
    """Test default rental query generation."""
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    flt = RentalFilter()
    params = builder.build_query_parameters(flt)

    assert params["neg"] == "locacao"
    assert params["por_pagina"] == "10"
    assert params["pagina"] == "0"
    assert params["ordenar"] == "menor_valor"
    assert params["cidade_id"] == ""


def test_target_url_reproduction():
    """Test reproducing the user prompt target URL parameters."""
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    # Target URL: neg=&tipo=&cidade_id=&bairro=&condominio_id=&valor=&dormitorios=1&suites=0&garagens=0&ref=&submit=
    flt = (
        RentalFilter()
        .with_transaction("")
        .with_bedrooms(1)
        .with_suites(0)
        .with_garages(0)
    )
    url = builder.build_search_url(flt)
    assert "dormitorios=1" in url
    assert "neg=" in url


def test_custom_filters_query():
    """Test query generation with custom city, neighborhood, price, and pagination."""
    config = PortalMGConfiguration()
    builder = RentalQueryBuilder(config)
    flt = (
        RentalFilter()
        .with_city("2371")
        .with_neighborhood("Centro")
        .with_category("2")
        .with_bedrooms(3)
        .with_price_range(1000.0, 2500.0)
        .with_page(2)
        .with_page_size(20)
        .with_sort("maior_valor")
    )
    params = builder.build_query_parameters(flt)

    assert params["cidade_id"] == "2371"
    assert params["bairro"] == "Centro"
    assert params["tipo"] == "2"
    assert params["dormitorios"] == "3"
    assert params["valor"] == "1000-2500.00"
    assert params["por_pagina"] == "20"
    assert params["pagina"] == "20"  # (page 2 - 1) * 20
    assert params["ordenar"] == "maior_valor"
