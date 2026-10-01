"""CLI script for discovering search facets on Portal Imóveis MG."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.providers.portalmg import PortalMGRentalProvider


def main() -> None:
    """Fetch and print available search facets."""
    provider = PortalMGRentalProvider.create_default()
    facets = provider.get_facets()
    cities = facets.cities()
    neighborhoods = facets.neighborhoods()
    categories = facets.categories()

    print(f"\nFacetas do Portal Imóveis MG:")
    print("=" * 60)
    print(f"Cidades disponíveis ({len(cities)}):")
    for c in cities:
        print(f"  [{c.city_id:>4}] {c.name}")
    print("-" * 60)
    print(f"Categorias / Subtipos ({len(categories)}):")
    for k in categories:
        print(f"  [{k.category_id:>3}] {k.name}")
    print("-" * 60)
    print(f"Bairros cadastrados ({len(neighborhoods)}):")
    for n in neighborhoods[:15]:
        print(f"  • {n.name}")
    if len(neighborhoods) > 15:
        print(f"  ... e mais {len(neighborhoods) - 15} bairros")
    print("=" * 60)


if __name__ == "__main__":
    main()
