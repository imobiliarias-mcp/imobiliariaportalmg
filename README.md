# Portal Imóveis MG — Central Rental Research MCP Module

Reverse-engineered rental search provider and domain client for **Portal Imóveis MG** (`https://www.imobiliariaportalmg.com.br`, CRECI MGJ 5595), designed as a modular integration for a **Central Rental Research MCP (Model Context Protocol)**.

## 1. Project Overview

This repository reverse-engineers the search, filter, pagination, taxonomy aggregation, and property detail APIs of Portal Imóveis MG (built on the **Orangeimob** SaaS real estate engine).

- **API Specification Document**: [`docs/api-research.md`](file:///home/samuelcaldas/repos/imobiliarias/imobiliariaportalmg/docs/api-research.md)
- **Research Plan & Findings**: [`scripts/research-plan.md`](file:///home/samuelcaldas/repos/imobiliarias/imobiliariaportalmg/scripts/research-plan.md)
- **Architecture & Calisthenics**: [`scripts/ARCHITECTURE.md`](file:///home/samuelcaldas/repos/imobiliarias/imobiliariaportalmg/scripts/ARCHITECTURE.md)
- **CLI & Integration Guide**: [`scripts/USAGE.md`](file:///home/samuelcaldas/repos/imobiliarias/imobiliariaportalmg/scripts/USAGE.md)

---

## 2. Core Capabilities

1. **Target Search Reproduction**:
   Reproduces the baseline search:
   `https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?neg=&tipo=&cidade_id=&bairro=&condominio_id=&valor=&dormitorios=1&suites=0&garagens=0&ref=&submit=`
2. **Rental Search**:
   Restricts search to active rentals using `neg=locacao`, with multi-dimensional filtering (city, neighborhood, categories, price range, bedrooms, suites, parking).
3. **Offset Pagination**:
   Calculates exact zero-based offset `pagina = (page - 1) * por_pagina` with graceful termination when out-of-bounds.
4. **Property Detail & Microdata**:
   Retrieves Schema.org JSON-LD microdata, physical specs (bedrooms, suites, bathrooms, area), condo fees, IPTU, amenities, and AWS S3 photo gallery.
5. **Dynamic AJAX Taxonomy**:
   Discovers municipal neighborhoods and sub-types via `POST /ajax.php?function=get_bairros_json` and `POST /ajax.php?function=get_subtipos_json`.
6. **Central MCP Integration**:
   Implements `RentalProviderProtocol` and provides `PortalMGMcpAdapter` for plug-and-play MCP tool execution.

---

## 3. Quick Start

### 3.1 Setup Environment
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 3.2 Run Automated Tests
```bash
.venv/bin/python scripts/run_tests.py
```

### 3.3 Run Live Verification
```bash
.venv/bin/python scripts/verify_research.py
```

### 3.4 CLI Commands
```bash
# Search rentals in Timóteo
.venv/bin/python scripts/run_search.py --city 2371 --neighborhood Centro

# Get full property details
.venv/bin/python scripts/run_property_detail.py --id 608

# Discover search facets
.venv/bin/python scripts/run_facets.py
```
