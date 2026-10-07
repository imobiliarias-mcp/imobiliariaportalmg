"""HTML and JSON response parsers for Portal Imóveis MG."""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from scripts.domain.collections import (
    CategoryItem,
    CityItem,
    NeighborhoodItem,
    RentalSearchResult,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingFinancials,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    RentalPropertyDetail,
    RentalPropertySummary,
)
from scripts.domain.exceptions import ParsingException, PropertyNotFoundException
from scripts.domain.value_objects import ListingPrice, PropertyCode


class SearchResultParser:
    """Parses search results HTML into domain collections."""

    def __init__(
        self, public_base_url: str = "https://www.imobiliariaportalmg.com.br"
    ) -> None:
        """Configure the public property-link base URL."""
        parsed_url = urlsplit(public_base_url.strip())
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Public base URL must use HTTP(S) and include a host")
        if parsed_url.query or parsed_url.fragment:
            raise ValueError("Public base URL cannot contain a query or fragment")
        self._public_base_url = public_base_url.rstrip("/") + "/"

    def _resolve_public_url(self, href: str, property_id: str) -> str:
        """Resolve a listing link and reject unsafe schemes with property context."""
        relative_url = href or f"imoveis_detalhes.php?id={property_id}"
        try:
            public_url = urljoin(self._public_base_url, relative_url.strip())
            parsed_url = urlsplit(public_url)
        except ValueError as exc:
            raise ParsingException(
                f"Invalid public property URL for listing {property_id}: {href}"
            ) from exc
        if not self._is_property_url(parsed_url, property_id):
            raise ParsingException(
                f"Invalid public property URL for listing {property_id}: {href}"
            )
        return public_url

    def _is_property_url(self, parsed_url, property_id: str) -> bool:
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return False
        if parsed_url.netloc.lower() != urlsplit(self._public_base_url).netloc.lower():
            return False
        expected_path = urlsplit(self._public_base_url).path.rstrip("/")
        if parsed_url.path != f"{expected_path}/imoveis_detalhes.php":
            return False
        query_parameters = dict(
            parameter.split("=", 1) if "=" in parameter else (parameter, "")
            for parameter in parsed_url.query.split("&")
        )
        return query_parameters.get("id") == property_id

    def _extract_total_count(self, soup: BeautifulSoup) -> int:
        """Extract total listing count from header quantity."""
        qtd_el = soup.find(class_="imoveis-listagem__header-quantidade")
        if not qtd_el:
            return 0
        match = re.search(r"(\d+)", qtd_el.text)
        return int(match.group(1)) if match else 0

    def _extract_id_and_code(self, card: Tag) -> ListingIdentity:
        """Extract property ID and reference code."""
        link_el = card.find("a", href=True)
        href = link_el["href"] if link_el else ""
        match = re.search(r"id=(\d+)", href)
        prop_id = match.group(1) if match else "0"
        ref_el = card.find(class_="li-imovel__ref")
        raw_ref = ref_el.text.replace("REF", "").strip() if ref_el else prop_id
        return ListingIdentity(property_id=prop_id, reference=PropertyCode(raw_ref or prop_id))

    def _extract_price(self, card: Tag) -> ListingFinancials:
        """Extract monetary price from card."""
        val_el = card.find(class_="li-imovel__valor")
        if not val_el:
            return ListingFinancials(rental_price=ListingPrice(0.0))
        cleaned = re.sub(r"[^\d,]", "", val_el.text.strip()).replace(",", ".")
        amount = float(cleaned) if cleaned else 0.0
        return ListingFinancials(rental_price=ListingPrice(amount))

    def _extract_location(self, card: Tag) -> ListingLocation:
        """Extract neighborhood, city, and state."""
        bairro_el = card.find(class_="li-imovel__bairro")
        cidade_el = card.find(class_="li-imovel__cidade")
        estado_el = card.find(class_="li-imovel__estado")
        bairro = bairro_el.text.strip() if bairro_el else ""
        cidade = cidade_el.text.strip() if cidade_el else ""
        estado = estado_el.text.strip() if estado_el else "MG"
        return ListingLocation(neighborhood=bairro, city=cidade, state=estado)

    def _extract_card(self, card: Tag) -> RentalPropertySummary:
        """Parse single listing card into domain summary."""
        identity = self._extract_id_and_code(card)
        financials = self._extract_price(card)
        location = self._extract_location(card)
        cat_el = card.find(class_="li-imovel__categoria")
        img_el = card.find(class_="li-imovel__imagem")
        link_el = card.find(class_="li-imovel__link-informacoes")
        category = cat_el.text.strip() if cat_el else ""
        thumb = img_el.get("src", "") if img_el else ""
        detail = link_el.get("href", "") if link_el else ""
        public_url = self._resolve_public_url(detail, identity.property_id)
        core = ListingCore(identity=identity, financials=financials)
        details = ListingDetails(
            location=location,
            category=category,
            thumbnail_url=thumb,
            detail_url=detail or f"imoveis_detalhes.php?id={identity.property_id}",
            url=public_url,
        )
        return RentalPropertySummary(core=core, details=details)

    def parse_search_response(
        self,
        html_content: str,
        current_page: int = 1,
        page_size: int = 10,
    ) -> RentalSearchResult:
        """Parse complete search page HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        total_count = self._extract_total_count(soup)
        card_tags = soup.find_all(class_="li-imovel")
        summaries = [self._extract_card(c) for c in card_tags]
        return RentalSearchResult(
            items=summaries,
            total_count=total_count,
            current_page=current_page,
            page_size=page_size,
        )


class PropertyDetailParser:
    """Parses property detail page HTML and microdata."""

    def __init__(
        self, public_base_url: str = "https://www.imobiliariaportalmg.com.br"
    ) -> None:
        """Configure the public origin used for serialized property URLs."""
        parsed_url = urlsplit(public_base_url.strip())
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Public base URL must use HTTP(S) and include a host")
        if parsed_url.query or parsed_url.fragment:
            raise ValueError("Public base URL cannot contain a query or fragment")
        self._public_base_url = public_base_url.rstrip("/") + "/"

    def _relative_detail_url(self, property_id: str) -> str:
        """Build the documented relative detail route for a property."""
        return f"imoveis_detalhes.php?{urlencode({'id': property_id})}"

    def _resolve_public_url(self, property_id: str) -> str:
        """Build a public property URL without using the transport origin."""
        relative_path = self._relative_detail_url(property_id)
        return urljoin(self._public_base_url, relative_path)

    def _extract_json_ld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract and parse Schema.org JSON-LD microdata."""
        tag = soup.find("script", type="application/ld+json")
        if not tag or not tag.string:
            return {}
        try:
            return json.loads(tag.string)
        except Exception:
            return {}

    def _check_not_found(self, soup: BeautifulSoup) -> None:
        """Verify page represents a valid existing property."""
        h1 = soup.find("h1")
        if h1 and "não encontrado" in h1.text.lower():
            raise PropertyNotFoundException("Property not found on server.")
        title = soup.find(class_="imovel__titulo")
        if not title:
            raise PropertyNotFoundException("Property title container missing.")

    def _extract_specs(self, soup: BeautifulSoup) -> ListingSpecs:
        """Extract physical specs from characteristic list."""
        text = soup.get_text()
        bed_m = re.search(r"(?:Quartos|Dormitórios):\s*(\d+)", text, re.I)
        bath_m = re.search(r"Banheiros:\s*(\d+)", text, re.I)
        suite_m = re.search(r"(?:Suítes|Suíte):\s*(\d+)", text, re.I)
        gar_m = re.search(r"(?:Garagens|Vagas):\s*(\d+)", text, re.I)
        area_m = re.search(r"Área(?:\s+\w+)?:\s*([\d.,]+)\s*m²", text, re.I)
        return ListingSpecs(
            bedrooms=int(bed_m.group(1)) if bed_m else 0,
            bathrooms=int(bath_m.group(1)) if bath_m else 0,
            suites=int(suite_m.group(1)) if suite_m else 0,
            garages=int(gar_m.group(1)) if gar_m else 0,
            area_text=f"{area_m.group(1)} m²" if area_m else "",
        )

    def _extract_fee_from_text(self, text: str, pattern: str) -> Optional[ListingPrice]:
        """Extract monetary fee from text using regex pattern."""
        match = re.search(pattern, text, re.I)
        if not match:
            return None
        clean = match.group(1).replace(".", "").replace(",", ".")
        return ListingPrice(float(clean))

    def _extract_financials(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> ListingFinancials:
        """Extract price, condo fee, and IPTU."""
        val_el = soup.find(class_="imovel__valor-valor")
        amount = 0.0
        if val_el:
            cleaned = re.sub(r"[^\d,]", "", val_el.text.strip()).replace(",", ".")
            amount = float(cleaned) if cleaned else 0.0
        text = soup.get_text()
        condo_fee = self._extract_fee_from_text(text, r"Condomínio:\s*R\$\s*([\d.,]+)")
        iptu = self._extract_fee_from_text(text, r"IPTU:\s*R\$\s*([\d.,]+)")
        return ListingFinancials(rental_price=ListingPrice(amount), condo_fee=condo_fee, iptu=iptu)

    def _extract_amenities(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> List[str]:
        """Extract amenity features."""
        about = json_ld.get("about", {})
        amenity_specs = about.get("amenityFeature", [])
        if amenity_specs:
            return [a["name"] for a in amenity_specs if "name" in a]
        container = soup.find(class_="imovel__caracteristicas2")
        if not container:
            return []
        items = container.get_text().split("√")
        return [i.strip() for i in items if i.strip() and "Características" not in i]

    def _extract_photos(self, soup: BeautifulSoup) -> List[str]:
        """Extract photo URLs from gallery."""
        photos = []
        links = soup.find_all(class_="imovel__foto-link")
        for link in links:
            href = link.get("href")
            if href and href not in photos:
                photos.append(href)
        return photos

    def parse_detail_response(self, html_content: str, property_id: str) -> RentalPropertyDetail:
        """Parse complete property detail HTML page."""
        soup = BeautifulSoup(html_content, "html.parser")
        self._check_not_found(soup)
        json_ld = self._extract_json_ld(soup)
        identity = ListingIdentity(property_id=property_id, reference=PropertyCode(property_id))
        financials = self._extract_financials(soup, json_ld)
        specs = self._extract_specs(soup)
        amenities = self._extract_amenities(soup, json_ld)
        photos = self._extract_photos(soup)
        thumb = photos[0] if photos else ""
        location = ListingLocation(neighborhood="", city="")
        core = ListingCore(identity=identity, financials=financials)
        relative_url = self._relative_detail_url(property_id)
        public_url = self._resolve_public_url(property_id)
        details = ListingDetails(
            location=location,
            category="",
            thumbnail_url=thumb,
            detail_url=relative_url,
            url=public_url,
        )
        summary = RentalPropertySummary(core=core, details=details)
        profile = DetailedProfile(specs=specs, amenities=amenities, photos=photos)
        return RentalPropertyDetail(summary=summary, profile=profile)


class FacetParser:
    """Parses AJAX taxonomy responses and HTML selects."""

    def parse_neighborhoods(self, json_content: str, city_id: str = "") -> List[NeighborhoodItem]:
        """Parse JSON response from get_bairros_json."""
        try:
            data = json.loads(json_content)
            items = []
            for entry in data:
                label = entry.get("label", "").strip()
                if label:
                    items.append(NeighborhoodItem(name=label, city_id=city_id))
            return items
        except Exception as exc:
            raise ParsingException(f"Failed to parse neighborhoods JSON: {exc}") from exc

    def parse_categories(self, json_content: str) -> List[CategoryItem]:
        """Parse JSON response from get_subtipos_json."""
        try:
            data = json.loads(json_content)
            items = []
            for entry in data:
                val = str(entry.get("value", "")).strip()
                label = entry.get("label", "").strip()
                if val and label:
                    items.append(CategoryItem(category_id=val, name=label))
            return items
        except Exception as exc:
            raise ParsingException(f"Failed to parse categories JSON: {exc}") from exc

    def parse_cities_from_html(self, html_content: str) -> List[CityItem]:
        """Parse city options from search form HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        select = soup.find(id="sl-cidade")
        if not select:
            return []
        items = []
        for opt in select.find_all("option"):
            cid = opt.get("value", "").strip()
            name = opt.text.strip()
            if cid and name:
                items.append(CityItem(city_id=cid, name=name))
        return items
