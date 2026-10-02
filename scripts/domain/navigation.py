"""Public navigation metadata for rental property listings."""

from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from scripts.domain.exceptions import ValidationException


@dataclass(frozen=True)
class ListingNavigation:
    """Source detail path and normalized public property link."""

    detail_url: str = ""
    url: str = ""

    def validate_for(self, property_id: str) -> None:
        """Reject invalid public property links with listing context."""
        try:
            parsed_url = urlsplit(self.url)
            query_parameters = parse_qs(parsed_url.query)
        except ValueError as exc:
            raise ValidationException(
                f"Invalid public property URL for listing {property_id}"
            ) from exc
        is_property_route = parsed_url.path.rsplit("/", 1)[-1] == "imoveis_detalhes.php"
        has_matching_id = query_parameters.get("id") == [property_id]
        is_absolute = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)
        if not is_absolute or not is_property_route or not has_matching_id:
            raise ValidationException(
                f"A valid public property URL is required for listing {property_id}"
            )
