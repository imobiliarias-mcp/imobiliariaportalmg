"""HTML and JSON response parsers for Portal Imóveis MG."""

import json
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from scripts.domain.collections import (
    CategoryItem,
    CityItem,
    FacetCollection,
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
        detail = link_el.get("href", "") if link_el else f"imoveis_detalhes.php?id={identity.property_id}"
        core = ListingCore(identity=identity, financials=financials)
        details = ListingDetails(location=location, category=category, thumbnail_url=thumb, detail_url=detail)
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

    def _extract_financials(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> ListingFinancials:
        """Extract price and condo fee."""
        val_el = soup.find(class_="imovel__valor-valor")
        amount = 0.0
        if val_el:
            cleaned = re.sub(r"[^\d,]", "", val_el.text.strip()).replace(",", ".")
            amount = float(cleaned) if cleaned else 0.0
        condo_fee = None
        condo_m = re.search(r"Condomínio:\s*R\$\s*([\d.,]+)", soup.get_text(), re.I)
        if condo_m:
            condo_clean = condo_m.group(1).replace(".", "").replace(",", ".")
            condo_fee = ListingPrice(float(condo_clean))
        return ListingFinancials(rental_price=ListingPrice(amount), condo_fee=condo_fee)

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
        details = ListingDetails(location=location, category="", thumbnail_url=thumb)
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
