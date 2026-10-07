"""Unit tests for response parsers."""

import pytest
from scripts.client.parsers import (
    FacetParser,
    PropertyDetailParser,
    SearchResultParser,
)
from scripts.domain.exceptions import ParsingException, PropertyNotFoundException

SAMPLE_SEARCH_HTML = """
<div class="imoveis-listagem__header-quantidade">
    2 imóveis encontrado(s)
</div>
<ul class="lista-imoveis">
    <li class="li-imovel">
        <div class="li-imovel__imagem-container">
            <a class="li-imovel__imagem-link" href="imoveis_detalhes.php?id=608">
                <img class="li-imovel__imagem" src="https://s3.amazonaws.com/test/thumb1.jpg" />
                <span class="li-imovel__ref">REF 608</span>
            </a>
        </div>
        <div class="li-imovel__descricao">
            <h3 class="li-imovel__titulo">
                <a href="imoveis_detalhes.php?id=608">
                    <span class="li-imovel__categoria">Casas</span>
                    <span class="li-imovel__extra">
                        <span class="li-imovel__bairro">Bromélias</span>
                        <span class="li-imovel__cidade">Timóteo</span>
                        <span class="li-imovel__estado">MG</span>
                    </span>
                </a>
            </h3>
            <p class="li-imovel__valores">
                <span class="li-imovel__valor-rotulo">Locação:</span>
                <span class="li-imovel__valor"><span>R$ 1.980,00</span></span>
            </p>
            <div class="li-imovel__mais-informacoes">
                <a class="li-imovel__link-informacoes" href="imoveis_detalhes.php?id=608">Mais</a>
            </div>
        </div>
    </li>
</ul>
"""

SAMPLE_DETAIL_HTML = """
<html>
<head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "RealEstateListing",
  "about": {
    "name": "Casas em Bromélias",
    "amenityFeature": [
      {"name": "Churrasqueira"},
      {"name": "Closet"}
    ]
  }
}
</script>
</head>
<body>
<h1 class="imovel__titulo">REF: 608 – Casas Bromélias – Timóteo – MG</h1>
<span class="imovel__valor-valor">R$ 1.980,00</span>
<ul class="imovel__caracteristicas">
    <li>Quartos: 3</li>
    <li>Banheiros: 2</li>
    <li>Suítes: 1</li>
    <li>Garagens: 2</li>
    <li>Área útil: 180.00 m²</li>
    <li>Condomínio: R$ 250,00</li>
    <li>IPTU: R$ 85,00</li>
</ul>
<ul class="imovel__galeria">
    <li><a class="imovel__foto-link" href="https://s3.amazonaws.com/test/photo1.jpg">Photo 1</a></li>
    <li><a class="imovel__foto-link" href="https://s3.amazonaws.com/test/photo2.jpg">Photo 2</a></li>
</ul>
</body>
</html>
"""

SAMPLE_NOT_FOUND_HTML = """
<html>
<body>
<h1>Imóvel não encontrado</h1>
</body>
</html>
"""


def test_search_parser():
    """Test search result HTML parsing."""
    parser = SearchResultParser()
    result = parser.parse_search_response(SAMPLE_SEARCH_HTML, current_page=1, page_size=10)
    assert result.total_count() == 2
    assert len(result) == 1

    item = list(result)[0]
    assert item.id() == "608"
    assert item.ref() == "608"
    assert item.details.category == "Casas"
    assert item.details.location.neighborhood == "Bromélias"
    assert item.details.location.city == "Timóteo"
    assert item.price().amount() == 1980.0
    assert item.details.thumbnail_url == "https://s3.amazonaws.com/test/thumb1.jpg"


def test_search_parser_empty():
    """Test search result with empty HTML."""
    parser = SearchResultParser()
    result = parser.parse_search_response("<div>Nenhum imóvel encontrado</div>")
    assert result.total_count() == 0
    assert len(result) == 0


def test_property_detail_parser():
    """Test property detail HTML and microdata parsing."""
    parser = PropertyDetailParser()
    detail = parser.parse_detail_response(SAMPLE_DETAIL_HTML, property_id="608")
    assert detail.id() == "608"
    assert detail.ref() == "608"
    assert detail.summary.price().amount() == 1980.0
    assert detail.profile.specs.bedrooms == 3
    assert detail.profile.specs.bathrooms == 2
    assert detail.profile.specs.suites == 1
    assert detail.profile.specs.garages == 2
    assert detail.profile.specs.area_text == "180.00 m²"
    assert "Churrasqueira" in detail.profile.amenities
    assert len(detail.profile.photos) == 2
    assert detail.summary.core.financials.iptu is not None
    assert detail.summary.core.financials.iptu.amount() == 85.0
    assert detail.to_dictionary()["iptu"] == 85.0


def test_property_detail_not_found():
    """Test property detail parser raising PropertyNotFoundException."""
    parser = PropertyDetailParser()
    with pytest.raises(PropertyNotFoundException):
        parser.parse_detail_response(SAMPLE_NOT_FOUND_HTML, property_id="999")


def test_facet_parser():
    """Test taxonomy facet parsing."""
    parser = FacetParser()
    nb_json = '[{"label": "Centro", "value": "Centro"}, {"label": "Bromélias", "value": "Bromélias"}]'
    neighborhoods = parser.parse_neighborhoods(nb_json, city_id="2371")
    assert len(neighborhoods) == 2
    assert neighborhoods[0].name == "Centro"

    cat_json = '[{"label": "Apartamento Padrão", "value": "8"}]'
    categories = parser.parse_categories(cat_json)
    assert len(categories) == 1
    assert categories[0].name == "Apartamento Padrão"
    assert categories[0].category_id == "8"


def _parse_search_with_detail_href(href: str, public_base_url: str = "https://www.imobiliariaportalmg.com.br"):
    marker = 'href="imoveis_detalhes.php?id=608">Mais'
    html = SAMPLE_SEARCH_HTML.replace(marker, f'href="{href}">Mais')
    parser = SearchResultParser(public_base_url=public_base_url)
    result = parser.parse_search_response(html)
    return next(iter(result))


@pytest.mark.parametrize(
    ("href", "expected_url"),
    [
        (
            "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608",
            "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608",
        ),
        (
            "imoveis_detalhes.php?id=608&utm_campaign=rentals",
            "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608&utm_campaign=rentals",
        ),
        (
            "//www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608",
            "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608",
        ),
    ],
)
def test_search_resolves_property_links_and_preserves_legacy_path(href, expected_url):
    listing = _parse_search_with_detail_href(href)
    assert listing.details.url == expected_url
    assert listing.details.detail_url == href


def test_search_uses_configured_public_base_for_relative_property_link():
    listing = _parse_search_with_detail_href(
        "imoveis_detalhes.php?id=608", "https://public.example"
    )
    assert listing.details.url == "https://public.example/imoveis_detalhes.php?id=608"
    assert listing.details.detail_url == "imoveis_detalhes.php?id=608"


def test_search_uses_documented_detail_route_when_information_link_is_missing():
    marker = '<div class="li-imovel__mais-informacoes">\n                <a class="li-imovel__link-informacoes" href="imoveis_detalhes.php?id=608">Mais</a>\n            </div>'
    html = SAMPLE_SEARCH_HTML.replace(marker, "")
    listing = next(iter(SearchResultParser().parse_search_response(html)))
    assert listing.details.detail_url == "imoveis_detalhes.php?id=608"
    assert listing.details.url == "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608"


def test_search_rejects_invalid_property_scheme_with_listing_context():
    with pytest.raises(ParsingException, match="608"):
        _parse_search_with_detail_href("javascript:alert(1)")


def test_search_wraps_malformed_authority_with_listing_context():
    with pytest.raises(ParsingException, match="608"):
        _parse_search_with_detail_href("https://[::1")


@pytest.mark.parametrize(
    "href",
    [
        "https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?id=608",
        "https://www.imobiliariaportalmg.com.br/ajax.php?function=get_bairros_json",
        "https://cdn.example/thumb_608.jpg",
    ],
)
def test_search_rejects_non_property_routes_with_listing_context(href):
    with pytest.raises(ParsingException, match="608"):
        _parse_search_with_detail_href(href)


def test_search_serializes_public_url_without_changing_detail_url():
    listing = next(iter(SearchResultParser().parse_search_response(SAMPLE_SEARCH_HTML)))
    serialized = listing.to_dictionary()
    assert serialized["url"] == "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608"
    assert serialized["detail_url"] == "imoveis_detalhes.php?id=608"
