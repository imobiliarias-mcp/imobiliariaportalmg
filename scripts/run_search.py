"""CLI script for executing rental searches on Portal Imóveis MG."""

import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.criteria import RentalFilter
from scripts.providers.portalmg import PortalMGRentalProvider


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="Search rental properties on Portal Imóveis MG.")
    parser.add_argument("--city", type=str, default="", help="City ID (e.g. 2371 for Timóteo)")
    parser.add_argument("--neighborhood", type=str, default="", help="Neighborhood name (e.g. Centro)")
    parser.add_argument("--category", type=str, default="", help="Property Category ID (e.g. 2, 3, 6)")
    parser.add_argument("--bedrooms", type=int, default=0, help="Minimum number of bedrooms")
    parser.add_argument("--min-price", type=float, default=0.0, help="Minimum rental price in BRL")
    parser.add_argument("--max-price", type=float, default=0.0, help="Maximum rental price in BRL")
    parser.add_argument("--page", type=int, default=1, help="Page index (1-based)")
    parser.add_argument("--page-size", type=int, default=10, help="Page size (10, 20, 30)")
    parser.add_argument("--sort", type=str, default="menor_valor", help="Sort order (menor_valor, maior_valor)")
    return parser


def create_search_filter(arguments: argparse.Namespace) -> RentalFilter:
    """Translate command line arguments to domain RentalFilter."""
    working = RentalFilter().with_page(arguments.page).with_page_size(arguments.page_size)
    working = working.with_sort(arguments.sort)
    if arguments.city:
        working = working.with_city(arguments.city)
    if arguments.neighborhood:
        working = working.with_neighborhood(arguments.neighborhood)
    if arguments.category:
        working = working.with_category(arguments.category)
    if arguments.bedrooms > 0:
        working = working.with_bedrooms(arguments.bedrooms)
    if arguments.min_price > 0.0 or arguments.max_price > 0.0:
        working = working.with_price_range(arguments.min_price, arguments.max_price)
    return working


def display_results(result) -> None:
    """Print search summary and items to console."""
    total = result.total_count()
    returned = len(result)
    print(f"\nResultados: {returned} listados de {total} encontrados no Portal Imóveis MG")
    print(f"Página: {result.current_page()} de {result.total_pages()}\n")
    print("-" * 80)
    for listing in result:
        ref = listing.ref()
        cat = listing.details.category
        loc = listing.details.location.summary()
        price = listing.price().format_brl()
        print(f"[{ref}] {cat:<12} | {loc:<30} | {price}/mês")
    print("-" * 80)


def main() -> None:
    """Main execution function."""
    argument_parser = build_argument_parser()
    parsed_arguments = argument_parser.parse_args()
    search_filter = create_search_filter(parsed_arguments)
    provider = PortalMGRentalProvider.create_default()
    search_result = provider.search_rentals(search_filter)
    display_results(search_result)


if __name__ == "__main__":
    main()
