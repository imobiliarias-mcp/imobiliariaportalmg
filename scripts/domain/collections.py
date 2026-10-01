"""First-class domain collections for search results and facets."""

from dataclasses import dataclass
from typing import Iterator, List
from scripts.domain.entities import RentalPropertySummary


@dataclass(frozen=True)
class CityItem:
    """City taxonomy entry."""

    city_id: str
    name: str


@dataclass(frozen=True)
class NeighborhoodItem:
    """Neighborhood taxonomy entry."""

    name: str
    city_id: str = ""


@dataclass(frozen=True)
class CategoryItem:
    """Property category taxonomy entry."""

    category_id: str
    name: str


class RentalSearchResult:
    """First-class collection representing rental search results."""

    def __init__(
        self,
        items: List[RentalPropertySummary],
        total_count: int,
        current_page: int = 1,
        page_size: int = 10,
    ) -> None:
        """Initialize search result collection."""
        self._items = list(items)
        self._total_count = max(0, total_count)
        self._current_page = max(1, current_page)
        self._page_size = max(1, page_size)

    def __iter__(self) -> Iterator[RentalPropertySummary]:
        """Iterate over listings."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return number of listings on this page."""
        return len(self._items)

    def total_count(self) -> int:
        """Return total matching records across all pages."""
        return self._total_count

    def current_page(self) -> int:
        """Return current page number."""
        return self._current_page

    def total_pages(self) -> int:
        """Calculate total number of available pages."""
        if self._total_count == 0:
            return 1
        quotient, remainder = divmod(self._total_count, self._page_size)
        return quotient + 1 if remainder > 0 else quotient

    def has_next_page(self) -> bool:
        """Check if subsequent page exists."""
        return self._current_page < self.total_pages()

    def to_dictionary(self) -> dict:
        """Convert collection to dictionary representation for MCP tools."""
        return {
            "total_count": self._total_count,
            "current_page": self._current_page,
            "total_pages": self.total_pages(),
            "page_size": self._page_size,
            "has_next_page": self.has_next_page(),
            "listings": [item.to_dictionary() for item in self._items],
        }


class FacetCollection:
    """First-class collection of available filter options."""

    def __init__(
        self,
        cities: List[CityItem],
        neighborhoods: List[NeighborhoodItem],
        categories: List[CategoryItem],
    ) -> None:
        """Initialize facet collection."""
        self._cities = list(cities)
        self._neighborhoods = list(neighborhoods)
        self._categories = list(categories)

    def cities(self) -> List[CityItem]:
        """Return city facets."""
        return list(self._cities)

    def neighborhoods(self) -> List[NeighborhoodItem]:
        """Return neighborhood facets."""
        return list(self._neighborhoods)

    def categories(self) -> List[CategoryItem]:
        """Return category facets."""
        return list(self._categories)

    def to_dictionary(self) -> dict:
        """Convert facets to dictionary for MCP tools."""
        return {
            "cities": [{"id": c.city_id, "name": c.name} for c in self._cities],
            "neighborhoods": [{"name": n.name} for n in self._neighborhoods],
            "categories": [{"id": k.category_id, "name": k.name} for k in self._categories],
        }
