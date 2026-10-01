# Usage Guide: Portal Imóveis MG Rental Research

## 1. Quick Start with CLI Scripts

All scripts are executed from the repository root using the virtual environment:

### 1.1 Search Rentals (`scripts/run_search.py`)
```bash
# Default search (active rentals in Timóteo)
.venv/bin/python scripts/run_search.py

# Search rentals in Centro neighborhood
.venv/bin/python scripts/run_search.py --city 2371 --neighborhood Centro

# Search rentals with price ceiling of R$ 1.500
.venv/bin/python scripts/run_search.py --max-price 1500

# Search commercial rental properties (category 6)
.venv/bin/python scripts/run_search.py --category 6

# Pagination: page 2 with page size 10
.venv/bin/python scripts/run_search.py --page 2 --page-size 10
```

### 1.2 Property Details (`scripts/run_property_detail.py`)
```bash
# Retrieve full details, specs, amenities, and photo gallery for property 608
.venv/bin/python scripts/run_property_detail.py --id 608

# Retrieve commercial space details for property 547
.venv/bin/python scripts/run_property_detail.py --id 547
```

### 1.3 Discover Taxonomy & Facets (`scripts/run_facets.py`)
```bash
# List available cities, categories, and neighborhoods discovered from the portal
.venv/bin/python scripts/run_facets.py
```

### 1.4 End-to-End Verification (`scripts/verify_research.py`)
```bash
# Execute full live verification suite
.venv/bin/python scripts/verify_research.py
```

### 1.5 Automated Test Suite (`scripts/run_tests.py`)
```bash
# Run all unit and integration tests
.venv/bin/python scripts/run_tests.py
```

---

## 2. Programmatic Python API

### 2.1 Using `PortalMGRentalClient` (Central MCP Facade)

```python
from src.portalmg_research import PortalMGRentalClient

client = PortalMGRentalClient()

# Search rental listings
results = client.search_rentals(city_id="2371", neighborhood="Centro", max_price=2000.0)
print(f"Total matching listings: {results.total_count()}")

for listing in results:
    print(f"[{listing.ref()}] {listing.details.category} - {listing.price().format_brl()}")

# Get full property details
detail = client.get_details("608")
print(f"Property: {detail.ref()} | Rent: {detail.summary.price().format_brl()}")
print(f"Amenities: {detail.profile.amenities}")
print(f"Gallery photos: {len(detail.profile.photos)}")
```

### 2.2 Using `PortalMGMcpAdapter` (MCP Tool Registry)

```python
from scripts.mcp.tools import PortalMGMcpAdapter

adapter = PortalMGMcpAdapter.create_default()

# Tool: search_rentals
search_payload = adapter.search_rentals(city_id="2371", max_price=1500.0, page=1)
print(f"Total results: {search_payload['total_count']}")

# Tool: get_property_detail
detail_payload = adapter.get_property_detail("608")
print(f"Reference: {detail_payload['reference']}, Price: {detail_payload['rental_price']}")

# Tool: get_facets
facets_payload = adapter.get_facets()
print(f"Available cities: {len(facets_payload['cities'])}")
```
