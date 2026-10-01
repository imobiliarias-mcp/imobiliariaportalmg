"""CLI script for retrieving detailed property information on Portal Imóveis MG."""

import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.value_objects import PropertyCode
from scripts.providers.portalmg import PortalMGRentalProvider


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="Retrieve property details on Portal Imóveis MG.")
    parser.add_argument("--id", type=str, required=True, help="Property ID or Reference Code (e.g. 608)")
    return parser


def display_detail(detail) -> None:
    """Print complete property detail to console."""
    ref = detail.ref()
    prop_id = detail.id()
    price = detail.summary.price().format_brl()
    specs = detail.profile.specs
    amenities = detail.profile.amenities
    photos = detail.profile.photos
    condo = detail.summary.core.financials.condo_fee
    condo_str = condo.format_brl() if condo else "N/A"

    print(f"\nDetalhes do Imóvel [ID {prop_id} / REF {ref}] - Portal Imóveis MG")
    print("=" * 70)
    print(f"Aluguel:        {price}/mês")
    print(f"Condomínio:     {condo_str}")
    print(f"Quartos:        {specs.bedrooms}")
    print(f"Suítes:         {specs.suites}")
    print(f"Banheiros:      {specs.bathrooms}")
    print(f"Vagas garagem:  {specs.garages}")
    print(f"Área:           {specs.area_text or 'Não informada'}")
    print("-" * 70)
    print(f"Comodidades ({len(amenities)}):")
    for a in amenities:
        print(f"  • {a}")
    print("-" * 70)
    print(f"Fotos da Galeria ({len(photos)} fotos):")
    for i, p in enumerate(photos[:5]):
        print(f"  [{i+1}] {p}")
    if len(photos) > 5:
        print(f"  ... e mais {len(photos) - 5} fotos")
    print("=" * 70)


def main() -> None:
    """Main execution function."""
    parser = build_argument_parser()
    args = parser.parse_args()
    provider = PortalMGRentalProvider.create_default()
    code = PropertyCode(args.id)
    detail = provider.get_property_detail(code)
    display_detail(detail)


if __name__ == "__main__":
    main()
