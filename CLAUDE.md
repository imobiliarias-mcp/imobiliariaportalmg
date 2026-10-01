# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Environment Setup
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests
- **All tests**: `.venv/bin/pytest` or `.venv/bin/python scripts/run_tests.py`
- **Single test file**: `.venv/bin/pytest tests/test_domain.py`
- **Single test function**: `.venv/bin/pytest tests/test_domain.py -k test_property_code_valid`
- **Verbose output**: `.venv/bin/pytest -v`

### Live Research & Verification
- **Run live API verification**: `.venv/bin/python scripts/verify_research.py`
- **Search listings via CLI**: `.venv/bin/python scripts/run_search.py --city 2371 --neighborhood Centro`
- **Inspect property details**: `.venv/bin/python scripts/run_property_detail.py --id 608`
- **Discover taxonomy facets**: `.venv/bin/python scripts/run_facets.py`

---

## Architecture & Code Structure

This repository reverse-engineers the search, taxonomy, and property detail APIs of **Portal Imóveis MG** (`imobiliariaportalmg.com.br`, running on the **Orangeimob** SaaS engine) to provide a modular provider for a **Central Rental Research MCP (Model Context Protocol)**.

### Layer Separation

1. **MCP Boundary Facade** (`src/portalmg_research/`):
   - `PortalMGRentalClient`: High-level entry point exposing `.search()`, `.search_rentals()`, `.get_details()`, and `.get_facets()`, along with access to the underlying MCP adapter.

2. **Protocol Contracts** (`scripts/interfaces/`):
   - Segregated capability protocols: `RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`.
   - `RentalProviderProtocol`: Composed interface required for central MCP provider registration (`provider_name()`).

3. **MCP Tool Adapter** (`scripts/mcp/`):
   - `PortalMGMcpAdapter`: Formats and executes MCP tool calls (`search_rentals`, `get_property_detail`, `get_facets`, `get_provider_info`), returning dictionary payloads conforming to MCP tool schemas.

4. **Provider Implementation** (`scripts/providers/`):
   - `PortalMGRentalProvider`: Implements `RentalProviderProtocol` by orchestrating the HTTP transport, query builder, and HTML/JSON parsers.

5. **Client & Transport Layer** (`scripts/client/`):
   - `PortalMGConfiguration`: Base URLs, timeouts, and default headers.
   - `PortalMGHttpTransport`: Stateless `httpx.Client` wrapper for GET/POST requests.
   - `RentalQueryBuilder`: Assembles Orangeimob query strings from domain criteria (`RentalFilter`), computing zero-based offset pagination (`pagina = (page - 1) * por_pagina`).
   - `SearchResultParser`: Extracts listing cards, prices, specs, and pagination metadata from listing HTML.
   - `PropertyDetailParser`: Extracts Schema.org JSON-LD microdata, specs, amenities, and S3 gallery images from detail pages.
   - `FacetParser`: Extracts cities from HTML select dropdowns and neighborhoods/categories from AJAX JSON endpoints (`/ajax.php?function=get_bairros_json`, `get_subtipos_json`).

6. **Domain Layer** (`scripts/domain/`):
   - **Value Objects** (`value_objects.py`): Immutable, validated domain primitives (`PropertyCode`, `ListingPrice`, `RoomCount`, `PageOffset`, `PriceRange`).
   - **Criteria** (`criteria.py`): Immutable filter builder (`RentalFilter`, composed of `ScopeCriteria` and `ConstraintCriteria`).
   - **Entities** (`entities.py`): Rich listing entities (`RentalListingSummary`, `RentalPropertyDetail`, `ListingLocation`, `DetailedProfile`).
   - **Collections** (`collections.py`): First-class collections (`RentalSearchResult`, `FacetCollection`).
   - **Exceptions** (`exceptions.py`): Domain-specific exceptions (`ValidationException`, `ExtractionException`, `TransportException`).

---

## Design Standards & Constraints

- **Object Calisthenics**:
  - Maximum 1 indentation level per method.
  - No `else` keyword (use guard clauses, early returns, or polymorphism).
  - Wrap domain primitives in dedicated Value Objects.
  - First-class collections (collections contain no other state).
  - One dot per line (Law of Demeter; assign intermediate variables).
  - No abbreviations in variable/class/method names.
  - Small entities: methods ≤ 15 lines, classes ≤ 100 lines, files < 200 lines.
  - Maximum 2 instance variables per class (use composed collaborator objects).
  - Tell, don't ask: expose behavior and serializers rather than raw mutable state.
- **Orangeimob Specifics**:
  - Rental search requires `neg=locacao`.
  - Pagination uses zero-based offset: `pagina = (page - 1) * por_pagina`. Supported page sizes: 10, 20, 30.
  - Price ranges format as `{min}-{max}` with `.00` (e.g., `1001-2000.00`) or `{min}-i` for unbounded upper limits (e.g., `1501-i`).
  - Timóteo city ID is `2371` (Coronel Fabriciano `1778`, Ipatinga `1921`).

---

## Key References

- `docs/api-research.md`: Full reverse-engineered HTTP parameter matrix, endpoints, and microdata schema.
- `scripts/ARCHITECTURE.md`: Calisthenics mapping, SOLID compliance, and design patterns.
- `scripts/USAGE.md`: Detailed CLI script flags and programmatic SDK usage examples.
