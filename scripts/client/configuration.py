"""Client configuration and endpoint settings for Portal Imóveis MG."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointRoutes:
    """Internal URL route paths."""

    search_path: str = "/imoveis_listagem.php"
    detail_path: str = "/imoveis_detalhes.php"
    ajax_path: str = "/ajax.php"


@dataclass(frozen=True)
class PortalMGConfiguration:
    """Configuration settings for HTTP communications."""

    base_url: str = "https://www.imobiliariaportalmg.com.br"
    routes: EndpointRoutes = EndpointRoutes()
    timeout_seconds: float = 20.0
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    public_base_url: str = "https://www.imobiliariaportalmg.com.br"

    def search_url(self) -> str:
        """Construct full search endpoint URL."""
        return f"{self.base_url}{self.routes.search_path}"

    def detail_url(self, property_id: str) -> str:
        """Construct full property detail URL."""
        return f"{self.base_url}{self.routes.detail_path}?id={property_id}"

    def ajax_url(self, function_name: str) -> str:
        """Construct full AJAX endpoint URL with function name."""
        return f"{self.base_url}{self.routes.ajax_path}?function={function_name}"
