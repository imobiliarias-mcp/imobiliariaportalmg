"""Domain value objects for rental properties."""

from scripts.domain.exceptions import ValidationException


class PropertyCode:
    """Encapsulates property reference identifier."""

    def __init__(self, code: str) -> None:
        """Initialize and validate property code."""
        cleaned = str(code).strip()
        if not cleaned:
            raise ValidationException("Property code must not be empty.")
        self._code = cleaned

    def value(self) -> str:
        """Return raw property code."""
        return self._code

    def __str__(self) -> str:
        """Return string representation."""
        return self._code

    def __eq__(self, other: object) -> bool:
        """Check equality with another property code."""
        if not isinstance(other, PropertyCode):
            return False
        return self._code == other._code


class ListingPrice:
    """Encapsulates monetary price in BRL."""

    def __init__(self, amount: float) -> None:
        """Initialize and validate price value."""
        if amount < 0.0:
            raise ValidationException("Price amount must be non-negative.")
        self._amount = round(float(amount), 2)

    def amount(self) -> float:
        """Return numeric price value."""
        return self._amount

    def format_brl(self) -> str:
        """Format price as Brazilian Real string."""
        formatted = f"{self._amount:,.2f}"
        br_style = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {br_style}"

    def __eq__(self, other: object) -> bool:
        """Check equality with another price."""
        if not isinstance(other, ListingPrice):
            return False
        return self._amount == other._amount


class RoomCount:
    """Encapsulates bedroom, suite, or bathroom count."""

    def __init__(self, count: int) -> None:
        """Initialize and validate room count."""
        if count < 0:
            raise ValidationException("Room count must be non-negative.")
        self._count = int(count)

    def count(self) -> int:
        """Return numeric count."""
        return self._count

    def __eq__(self, other: object) -> bool:
        """Check equality with another count."""
        if not isinstance(other, RoomCount):
            return False
        return self._count == other._count


class PageOffset:
    """Encapsulates pagination offset and page size."""

    def __init__(self, page: int = 1, page_size: int = 10) -> None:
        """Initialize and validate pagination."""
        if page < 1:
            raise ValidationException("Page number must be at least 1.")
        if page_size not in (10, 20, 30):
            raise ValidationException("Page size must be 10, 20, or 30.")
        self._page = page
        self._page_size = page_size

    def page_number(self) -> int:
        """Return 1-indexed page number."""
        return self._page

    def page_size(self) -> int:
        """Return listings per page."""
        return self._page_size

    def calculate_offset(self) -> int:
        """Calculate zero-based offset parameter for Orangeimob."""
        return (self._page - 1) * self._page_size


class PriceRange:
    """Encapsulates search price range with optional upper boundary."""

    def __init__(self, minimum: float = 0.0, maximum: float = 0.0) -> None:
        """Initialize price range."""
        if minimum < 0.0:
            raise ValidationException("Minimum price must be non-negative.")
        if 0.0 < maximum < minimum:
            raise ValidationException("Maximum price must be greater than minimum.")
        self._min = round(float(minimum), 2)
        self._max = round(float(maximum), 2)

    def minimum(self) -> float:
        """Return minimum price."""
        return self._min

    def maximum(self) -> float:
        """Return maximum price."""
        return self._max

    def is_unbounded(self) -> bool:
        """Check if range is unbounded above."""
        return self._max <= 0.0

    def format_query_param(self) -> str:
        """Format range string for Orangeimob valor query parameter."""
        min_str = f"{int(self._min)}" if self._min.is_integer() else f"{self._min:.2f}"
        if self._min <= 0.0 and self._max <= 0.0:
            return ""
        if self.is_unbounded():
            return f"{min_str}-i"
        return f"{min_str}-{self._max:.2f}"
