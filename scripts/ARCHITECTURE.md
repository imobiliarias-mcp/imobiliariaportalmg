# Central Rental Research MCP Architecture & Design Standards — Portal Imóveis MG

## 1. Context: Central Rental Research MCP

The **Central Rental Research MCP** unifies rental search capabilities across various regional real estate agencies and SaaS engines into a coherent, standardized interface.

In this architecture, each agency portal functions as an isolated provider implementing a shared capability contract (`RentalProviderProtocol`). The **Portal Imóveis MG** module encapsulates all interactions with the **Orangeimob SaaS Engine** (`imoveis_listagem.php`, `imoveis_detalhes.php`, `ajax.php`), translating between Orangeimob's parameter conventions and clean domain models.

---

## 2. Priority Hierarchy

In accordance with system specifications, development rigorously adheres to this priority order:
1. **Correctness First**: Verified live HTTP interactions, accurate parameter encoding, robust Schema.org JSON-LD microdata extraction, and graceful error handling.
2. **Modularity Second**: Independent domain models, separated HTTP transport, dedicated parsers, and distinct MCP adapters.
3. **Style Principles Third**:
   - Strict SOLID principles.
   - Object Calisthenics constraints.
   - Design Patterns (Adapter, Strategy, Builder, Factory).

---

## 3. Object Calisthenics Compliance

Every module and class in `scripts/` and `src/portalmg_research/` adheres to the 9 rules of Object Calisthenics:

### Rule 1: Only One Level of Indentation per Method
Complex nested loops or branches are decomposed into dedicated helper methods.

### Rule 2: Don't Use the `else` Keyword
Zero occurrences of `else` across the entire codebase. Control flow relies on early returns, guard clauses, and polymorphically dispatched handlers.

### Rule 3: Wrap All Primitives and Strings
Domain primitives are encapsulated in validated Value Objects:
- `ListingPrice`: Non-negative decimal amounts formatted as BRL currency (`R$ 1.980,00`).
- `PropertyCode`: Non-empty reference identifier.
- `RoomCount`: Non-negative integer for rooms, suites, and bathrooms.
- `PageOffset`: Page number and page size with offset calculation for Orangeimob (`(page - 1) * page_size`).
- `PriceRange`: Bounded and unbounded (`min-i`) price ranges for search queries.

### Rule 4: First-Class Collections
Classes holding collections contain no other state:
- `RentalSearchResult`: Wraps listing summaries with total match count and pagination math.
- `FacetCollection`: Wraps cities, neighborhoods, and category taxonomies.

### Rule 5: One Dot per Line
Adheres to the Law of Demeter. Intermediate variables are explicitly assigned to prevent chained dependencies.

### Rule 6: Don't Abbreviate
Descriptive names are utilized throughout (e.g. `RentalPropertyDetail`, `ListingLocation`, `PortalMGHttpTransport`).

### Rule 7: Keep All Entities Small
- Functions and methods: **≤ 15 lines**.
- Classes: **≤ 100 lines**.
- Modules / files: **< 200 lines**.

### Rule 8: No Classes with More Than 2 Instance Variables
Classes declare at most 2 member attributes. Complex models decompose into composed collaborator objects (`ListingCore`, `ListingDetails`, `DetailedProfile`, `ScopeCriteria`, `ConstraintCriteria`).

### Rule 9: No Getters / Setters Exposing Raw State (Tell, Don't Ask)
Objects expose domain behaviors, formatters (`format_brl()`, `format_query_param()`), and serializers (`to_dictionary()`) rather than passive data getters.

---

## 4. SOLID Principles Compliance

1. **Single Responsibility (SRP)**:
   - `PortalMGHttpTransport`: HTTP communication and header injection.
   - `RentalQueryBuilder`: Query parameter assembly and offset calculation.
   - `SearchResultParser`: HTML search card extraction.
   - `PropertyDetailParser`: JSON-LD and HTML spec deserialization.
   - `FacetParser`: AJAX JSON and HTML select parsing.
   - `PortalMGRentalProvider`: Orchestrator connecting transport and parsers.
   - `PortalMGMcpAdapter`: Exposes dictionary outputs conforming to MCP tool schemas.

2. **Open/Closed (OCP)**:
   The provider and transport depend on abstract protocols (`RentalProviderProtocol`, `HttpTransportProtocol`). New transport implementations (e.g. mock transports for unit testing) are introduced without modifying provider code.

3. **Liskov Substitution (LSP)**:
   `StubHttpTransport` in tests safely substitutes `PortalMGHttpTransport` without breaking provider invariants.

4. **Interface Segregation (ISP)**:
   Client capabilities are segregated into focused protocols: `RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`.

5. **Dependency Inversion (DIP)**:
   High-level modules depend on abstractions (Protocols) rather than concrete implementations. Dependencies are injected via constructors.
