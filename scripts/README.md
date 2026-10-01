# Central Rental Research MCP — Portal Imóveis MG Module

This package implements the **Portal Imóveis MG** rental search provider designed as a modular adapter for a **Central Rental Research MCP (Model Context Protocol)** server.

---

## 1. Architectural Highlights

- **SOLID Principles**: Single responsibility classes, interface segregation via Protocols, dependency inversion.
- **Strict Object Calisthenics**:
  - One indent level per method.
  - Zero `else` keywords (guard clauses and early returns only).
  - Wrapped primitives (Value Objects: `PropertyCode`, `ListingPrice`, `RoomCount`, `PageOffset`, `PriceRange`).
  - First-class collections (`RentalSearchResult`, `FacetCollection`).
  - One dot per line (Law of Demeter).
  - No abbreviations.
  - Entity size limits: functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines.
  - ≤ 2 instance variables per class.
  - Tell, Don't Ask encapsulation.
- **Design Patterns**: Adapter, Strategy, Builder, Value Object, First-Class Collection, Factory.
- **Fail Fast**: Immediate boundary validation on inputs, raising descriptive typed domain exceptions.

---

## 2. Directory Layout

```
scripts/
├── README.md               # Package overview and developer instructions
├── ARCHITECTURE.md         # Calisthenics & SOLID design adherence documentation
├── USAGE.md                # Usage examples and MCP integration guide
├── research-plan.md        # Comprehensive reverse-engineering research plan & logs
├── verify_research.py      # Standalone live verification runner
├── __init__.py
├── domain/                 # Pure domain layer
│   ├── __init__.py
│   ├── exceptions.py       # Domain exception hierarchy
│   ├── value_objects.py    # Immutable value objects (PropertyCode, ListingPrice, etc.)
│   ├── entities.py         # Domain models (RentalPropertySummary, RentalPropertyDetail)
│   ├── criteria.py         # RentalFilter immutable fluent builder
│   └── collections.py      # First-class collections (RentalSearchResult, FacetCollection)
├── interfaces/             # Port contracts (MCP Provider Protocols)
│   ├── __init__.py
│   └── provider.py         # RentalProviderProtocol interface
├── client/                 # Infrastructure & Orangeimob HTTP client
│   ├── __init__.py
│   ├── configuration.py    # Portal configuration & routes
│   ├── http_transport.py   # HTTP transport implementation
│   ├── query_builder.py    # Query parameter translator
│   └── parsers.py          # Search & detail HTML and JSON parsers
├── providers/              # Adapter layer
│   ├── __init__.py
│   └── portalmg.py         # PortalMGRentalProvider implementation
├── mcp/                    # MCP tool contracts & handlers
│   ├── __init__.py
│   └── tools.py            # Central Rental Research MCP tool adapter
├── run_search.py           # CLI tool to run rental searches
├── run_property_detail.py  # CLI tool to fetch full property details
├── run_facets.py           # CLI tool to list search facets
└── run_tests.py            # Full test suite runner
```

---

## 3. Quick Run Commands

```bash
# Run automated unit tests
.venv/bin/python scripts/run_tests.py

# Run live integration verification
.venv/bin/python scripts/verify_research.py

# Run CLI search
.venv/bin/python scripts/run_search.py --city 2371 --neighborhood Centro
```
