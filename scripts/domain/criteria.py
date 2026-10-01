"""Search criteria and immutable filter definitions."""

from dataclasses import dataclass, replace
from scripts.domain.value_objects import PageOffset, PriceRange, RoomCount


@dataclass(frozen=True)
class LocationFilter:
    """Geographical filter attributes."""

    city_id: str = ""
    neighborhood: str = ""


@dataclass(frozen=True)
class PropertyFilter:
    """Physical property and typology constraints."""

    category_id: str = ""
    subcategory_id: str = ""
    bedrooms: int = 0
    suites: int = 0
    garages: int = 0
    reference: str = ""


@dataclass(frozen=True)
class ScopeCriteria:
    """Combines geographic and property attributes."""

    location: LocationFilter = LocationFilter()
    properties: PropertyFilter = PropertyFilter()


@dataclass(frozen=True)
class ConstraintCriteria:
    """Combines financial, pagination, and transaction settings."""

    price_range: PriceRange = PriceRange()
    pagination: PageOffset = PageOffset()
    transaction: str = "locacao"
    sort_order: str = "menor_valor"


@dataclass(frozen=True)
class RentalFilter:
    """Immutable rental search filter conforming to Orangeimob API."""

    scope: ScopeCriteria = ScopeCriteria()
    constraints: ConstraintCriteria = ConstraintCriteria()

    def with_city(self, city_id: str) -> "RentalFilter":
        """Return filter copy with target city ID."""
        new_loc = replace(self.scope.location, city_id=str(city_id).strip())
        new_scope = replace(self.scope, location=new_loc)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_neighborhood(self, neighborhood: str) -> "RentalFilter":
        """Return filter copy with target neighborhood name."""
        new_loc = replace(self.scope.location, neighborhood=str(neighborhood).strip())
        new_scope = replace(self.scope, location=new_loc)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_category(self, category_id: str) -> "RentalFilter":
        """Return filter copy with property category ID."""
        new_prop = replace(self.scope.properties, category_id=str(category_id).strip())
        new_scope = replace(self.scope, properties=new_prop)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_bedrooms(self, count: int) -> "RentalFilter":
        """Return filter copy with minimum bedrooms."""
        rc = RoomCount(count)
        new_prop = replace(self.scope.properties, bedrooms=rc.count())
        new_scope = replace(self.scope, properties=new_prop)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_suites(self, count: int) -> "RentalFilter":
        """Return filter copy with minimum suites."""
        rc = RoomCount(count)
        new_prop = replace(self.scope.properties, suites=rc.count())
        new_scope = replace(self.scope, properties=new_prop)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_garages(self, count: int) -> "RentalFilter":
        """Return filter copy with minimum garages."""
        rc = RoomCount(count)
        new_prop = replace(self.scope.properties, garages=rc.count())
        new_scope = replace(self.scope, properties=new_prop)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_reference(self, reference: str) -> "RentalFilter":
        """Return filter copy with reference code."""
        new_prop = replace(self.scope.properties, reference=str(reference).strip())
        new_scope = replace(self.scope, properties=new_prop)
        return RentalFilter(scope=new_scope, constraints=self.constraints)

    def with_price_ceiling(self, max_price: float) -> "RentalFilter":
        """Return filter copy with maximum price ceiling."""
        new_range = PriceRange(minimum=0.0, maximum=max_price)
        new_const = replace(self.constraints, price_range=new_range)
        return RentalFilter(scope=self.scope, constraints=new_const)

    def with_price_range(self, min_price: float, max_price: float) -> "RentalFilter":
        """Return filter copy with bounded price range."""
        new_range = PriceRange(minimum=min_price, maximum=max_price)
        new_const = replace(self.constraints, price_range=new_range)
        return RentalFilter(scope=self.scope, constraints=new_const)

    def with_page(self, page_number: int) -> "RentalFilter":
        """Return filter copy with page number."""
        curr_size = self.constraints.pagination.page_size()
        new_pag = PageOffset(page=page_number, page_size=curr_size)
        new_const = replace(self.constraints, pagination=new_pag)
        return RentalFilter(scope=self.scope, constraints=new_const)

    def with_page_size(self, page_size: int) -> "RentalFilter":
        """Return filter copy with page size limit."""
        curr_page = self.constraints.pagination.page_number()
        new_pag = PageOffset(page=curr_page, page_size=page_size)
        new_const = replace(self.constraints, pagination=new_pag)
        return RentalFilter(scope=self.scope, constraints=new_const)

    def with_transaction(self, transaction: str) -> "RentalFilter":
        """Return filter copy with transaction type."""
        new_const = replace(self.constraints, transaction=transaction)
        return RentalFilter(scope=self.scope, constraints=new_const)

    def with_sort(self, sort_order: str) -> "RentalFilter":
        """Return filter copy with sort order."""
        new_const = replace(self.constraints, sort_order=sort_order)
        return RentalFilter(scope=self.scope, constraints=new_const)
