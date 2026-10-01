# Reverse-Engineered API Specification: Portal Imóveis MG

## 1. Overview & Architecture

Portal Imóveis MG (`https://www.imobiliariaportalmg.com.br`) is a regional real estate agency portal based in Timóteo, Minas Gerais (CRECI MGJ 5595). The portal operates on the **Orangeimob** SaaS real estate engine (`orangeimob.com.br`, template `tema_2`).

The portal renders server-side HTML (charset `UTF-8`) served by an Apache web server. It features structured microdata (`Schema.org` JSON-LD), dynamic AJAX endpoints for taxonomy facets (neighborhoods and sub-types), and CDN-hosted media delivery on Amazon Web Services (AWS S3).

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All rental searches, filter queries, pagination offsets, property details, and AJAX taxonomy endpoints are publicly accessible without authentication, API keys, session tokens, or CSRF restrictions.
- **Session Cookies**: The server issues a standard `PHPSESSID` cookie, but state is not required; queries are completely stateless.
- **Request Headers**: Standard desktop `User-Agent` is recommended. The AJAX endpoints accept standard `application/x-www-form-urlencoded` payloads and optionally acknowledge `X-Requested-With: XMLHttpRequest`.
- **HTTP Methods**:
  - Search & Property Details: `GET`
  - AJAX Taxonomy Endpoints (`ajax.php`): `POST` (also responds to `GET`)

---

## 2. Rental & Search Endpoints

All property listing searches are routed through the central listing handler `imoveis_listagem.php`.

### 2.1 Canonical Search Endpoint

```http
GET /imoveis_listagem.php?neg={neg}&tipo={tipo}&cidade_id={cidade_id}&bairro={bairro}&condominio_id={condominio_id}&valor={valor}&dormitorios={dormitorios}&suites={suites}&garagens={garagens}&ref={ref}&por_pagina={por_pagina}&pagina={pagina}&ordenar={ordenar}&submit= HTTP/2
Host: www.imobiliariaportalmg.com.br
```

### 2.2 Target Rental Search URL Analysis
The baseline target URL specified for rental search investigation:
```
https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?neg=&tipo=&cidade_id=&bairro=&condominio_id=&valor=&dormitorios=1&suites=0&garagens=0&ref=&submit=
```
- **Reproduction**: Requesting the URL above performs a global search with a constraint of at least 1 bedroom (`dormitorios=1`).
- **Rental Restriction**: To restrict search exclusively to rental listings, set `neg=locacao`:
```
https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?neg=locacao&tipo=&cidade_id=&bairro=&condominio_id=&valor=&dormitorios=1&suites=0&garagens=0&ref=&submit=
```

---

## 3. Request Parameters & Filter Behavior

The search endpoint accepts parameter combinations via query string. The parameter matrix below details valid types, semantics, and observed system behavior:

| Parameter | Type | Example Values | Description & System Logic |
| :--- | :--- | :--- | :--- |
| `neg` | `string` | `locacao`, `venda`, `""` | **Transaction Type**.<br>• `locacao`: Rental properties.<br>• `venda`: Sales properties.<br>• empty: All transaction types. |
| `tipo` | `integer` | `2`, `3`, `4`, `5`, `6`, `7` | **Property Category ID**.<br>• `2`: Casas (Houses)<br>• `3`: Apartamentos (Apartments)<br>• `4`: Terrenos (Lots/Land)<br>• `5`: Galpões (Warehouses)<br>• `6`: Comerciais (Commercial Spaces/Offices)<br>• `7`: Rurais (Rural/Farms) |
| `subtipo` | `integer` | `8`, `9`, `10`, `14`, `17`, `27` | **Property Subcategory ID**.<br>• For `tipo=3`: `8` (Padrão), `9` (Cobertura), `16` (Loft), `17` (Flat), `27` (Kitchenette)<br>• For `tipo=2`: `10` (Padrão), `11` (Sobrado), `18` (Condomínio), `28` (Vila)<br>• For `tipo=6`: `14` (Sala Comercial), `23` (Prédio), `24` (Casa Comercial), `26` (Loja) |
| `cidade_id` | `integer` | `2371`, `1778`, `1921` | **City Numeric ID**.<br>• `2371`: Timóteo<br>• `1778`: Coronel Fabriciano<br>• `1921`: Ipatinga<br>• `1597`: Antônio Dias<br>• `1631`: Belo Oriente<br>• `1711`: Caratinga<br>• `1896`: Iapu<br>• `1959`: Jaguaraçu<br>• `2028`: Marliéria<br>• `2046`: Mesquita<br>• `2259`: Santana do Paraíso<br>• `2275`: São Domingos do Prata |
| `bairro` | `string` | `Centro`, `Bromélias`, `Timirim` | **Neighborhood Name**.<br>Matches the literal neighborhood string (case-insensitive in database query). Can also be supplied as array `bairro[]` when filtering multiple. |
| `condominio_id`| `integer` | `20`, `31`, `18`, `2` | **Condominium Numeric ID**.<br>• `20`: Alto do Giovanini<br>• `31`: casa<br>• `18`: Edifício Copesita<br>• `2`: Galeria Reis Magos<br>• `26`: Gardem<br>• `30`: Novo Horizonte<br>• `11`: Recanto Nobre Residence |
| `valor` | `string` | `1-1000.00`, `1001-2000.00`, `2001-2500.00`, `1501-i` | **Price Range Filter**.<br>Formatted as `{min}-{max}` where decimal values use `.00`.<br>• Unbounded upper limit uses `i` (infinity), e.g. `2501-i` or `1501-i`.<br>• Arbitrary numeric ranges (e.g. `500-1500.00`) are fully evaluated by the server. |
| `dormitorios` | `integer` | `0`, `1`, `2`, `3`, `4` | **Minimum Bedrooms**.<br>Filters listings having at least N bedrooms (`count >= N`). |
| `suites` | `integer` | `0`, `1`, `2` | **Minimum Suites**.<br>Filters listings having at least N suites (`count >= N`). |
| `garagens` | `integer` | `0`, `1`, `2` | **Minimum Parking Spaces**.<br>Filters listings having at least N garage slots (`count >= N`). |
| `ref` | `string` | `608`, `547`, `80` | **Reference Code Search**.<br>Exact or partial matching on listing reference code. |
| `por_pagina` | `integer` | `10`, `20`, `30` | **Page Size Limit**.<br>Number of listings returned per page. Supported presets are 10, 20, 30 (default is 10). |
| `pagina` | `integer` | `0`, `10`, `20`, `30` | **Pagination Row Offset**.<br>Calculated as `(page_number - 1) * por_pagina`. Default is `0`. |
| `ordenar` | `string` | `menor_valor`, `maior_valor` | **Sort Order**.<br>• `menor_valor`: Price ascending.<br>• `maior_valor`: Price descending. |
| `submit` | `string` | `""` | Form submission trigger parameter (optional). |

---

## 4. Supporting AJAX Endpoints

Orangeimob provides dedicated AJAX endpoints for dynamic cascading dropdowns and taxonomy discovery.

### 4.1 Neighborhood Lookup by City

```http
POST /ajax.php?function=get_bairros_json HTTP/2
Host: www.imobiliariaportalmg.com.br
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

cidade_id=2371
```

#### Response Format
Returns a JSON array of neighborhood objects:
```json
[
  {"label": "Alegre", "value": "Alegre"},
  {"label": "Alvorada", "value": "Alvorada"},
  {"label": "Bromélias", "value": "Bromélias"},
  {"label": "centro", "value": "centro"},
  {"label": "Funcionarios", "value": "Funcionarios"},
  {"label": "Quitandinha", "value": "Quitandinha"},
  {"label": "Santa Terezinha", "value": "Santa Terezinha"},
  {"label": "Timirim", "value": "Timirim"}
]
```
> [!NOTE]
> Omitting `cidade_id` returns the complete catalog of all active neighborhoods across all municipalities.

### 4.2 Subcategory Lookup by Category

```http
POST /ajax.php?function=get_subtipos_json HTTP/2
Host: www.imobiliariaportalmg.com.br
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

categoria_id=3
```

#### Response Format
Returns a JSON array of available subcategory types:
```json
[
  {"label": "Cobertura", "value": "9"},
  {"label": "Flat", "value": "17"},
  {"label": "Kitchenette", "value": "27"},
  {"label": "Loft", "value": "16"},
  {"label": "Padrão", "value": "8"}
]
```

---

## 5. Pagination Mechanics & Boundary Behavior

Pagination on Orangeimob utilizes an offset-based strategy controlled by `pagina` and `por_pagina`.

### 5.1 Offset Formula
$$\text{pagina} = (\text{page\_number} - 1) \times \text{por\_pagina}$$

- Page 1: `por_pagina=10&pagina=0` (or omitted)
- Page 2: `por_pagina=10&pagina=10`
- Page 3: `por_pagina=10&pagina=20`

### 5.2 DOM Pagination Indicators
1. **Total Count Indicator**:
   - Element selector: `.imoveis-listagem__header-quantidade`
   - Format: `"{N} imóveis encontrado(s)"` (e.g. `9 imóveis encontrado(s)`).
2. **Current Page & Total Pages**:
   - Container selector: `.paginacao`
   - Active page selector: `.paginacao__atual`
   - Format: `"Página: {current} de {total}"` (e.g. `Página: 1 de 1` or `Página: 2 de 12`).
3. **Navigation Links**:
   - Next page: `<a href="...&pagina={offset}">Próxima</a>`
   - Last page: `<a href="...&pagina={offset}">Última</a>`
   - Previous page: `<a href="...&pagina={offset}">Anterior</a>`
   - First page: `<a href="...&pagina={offset}">Primeira</a>`

### 5.3 Out-of-Bounds Behavior
- When an offset beyond available records is supplied (e.g. `pagina=9999`):
  - HTTP Status: `200 OK`
  - Total listing cards returned: `0`
  - Body container displays the message:
    ```html
    Nenhum imóvel encontrado.
    ```
- Safe termination condition: Client stops pagination when `len(cards) == 0` or when `current_page >= total_pages`.

---

## 6. Search Result Card Parsing

Listing cards are rendered inside `<ul class="lista-imoveis">` with item container `<li class="li-imovel">`.

### 6.1 Card DOM Structure
```html
<li class="li-imovel">
  <div class="li-imovel__imagem-container">
    <a class="li-imovel__imagem-link" href="imoveis_detalhes.php?id=547">
      <img class="li-imovel__imagem" src="https://s3.us-east-1.amazonaws.com/sgipro/703/thumb_112e8f685dcf1c856d89682d250edc78.jpg" alt="Imagem para o imóvel Ref. 547"/>
      <span class="li-imovel__ref">REF 547</span>
    </a>
  </div>
  <div class="li-imovel__descricao">
    <div class="li-imovel__descricao-dentro">
      <h3 class="li-imovel__titulo">
        <a href="imoveis_detalhes.php?id=547">
          <span class="li-imovel__categoria">Comerciais</span>
          <span class="li-imovel__extra">
            <span class="li-imovel__bairro">Centro</span>
            <span class="li-imovel__separador">–</span>
            <span class="li-imovel__cidade">Timóteo</span>
            <span class="li-imovel__separador">–</span>
            <span class="li-imovel__estado">MG</span>
          </span>
        </a>
      </h3>
      <ul class="li-imovel__caracteristicas">
        <li class="li-imovel__caracteristica"><i class="icone icone--quartos"></i><span>1</span></li>
        <li class="li-imovel__caracteristica"><i class="icone icone--banheiros"></i>1</li>
        <li class="li-imovel__caracteristica"><i class="icone icone--area"></i><span>45.00 m²</span></li>
      </ul>
      <p class="li-imovel__valores">
        <span class="li-imovel__valor-container li-imovel__valores--locacao">
          <span class="li-imovel__valor-rotulo">Locação:</span>
          <span class="li-imovel__valor"><span>R$ 1.200,00</span></span>
        </span>
      </p>
      <div class="li-imovel__mais-informacoes">
        <a class="li-imovel__link-informacoes" href="imoveis_detalhes.php?id=547">Mais informações</a>
      </div>
    </div>
  </div>
</li>
```

### 6.2 Field Extraction Matrix
| Target Field | Selector / Method | Example Extracted Value |
| :--- | :--- | :--- |
| `property_id` | `card.find("a", href=True)["href"]` regex `id=(\d+)` | `"547"` |
| `reference_code` | `span.li-imovel__ref` text replacing `"REF "` | `"547"` |
| `thumbnail_url` | `img.li-imovel__imagem["src"]` | `"https://s3.us-east-1.amazonaws.com/sgipro/703/thumb_..."` |
| `category` | `span.li-imovel__categoria` | `"Comerciais"` |
| `neighborhood` | `span.li-imovel__bairro` | `"Centro"` |
| `city` | `span.li-imovel__cidade` | `"Timóteo"` |
| `state` | `span.li-imovel__estado` | `"MG"` |
| `transaction_type`| `span.li-imovel__valor-rotulo` | `"Locação"` |
| `price_raw` | `span.li-imovel__valor` text | `"R$ 1.200,00"` |
| `price_amount` | Clean numeric parse (`1200.00`) | `1200.00` |
| `bedrooms` | `li-imovel__caracteristica` with `icone--quartos` | `1` |
| `bathrooms` | `li-imovel__caracteristica` with `icone--banheiros` | `1` |
| `suites` | `li-imovel__caracteristica` with `icone--suites` | `0` (or `None`) |
| `garage_slots` | `li-imovel__caracteristica` with `icone--garagens` | `0` (or `None`) |
| `area_text` | `li-imovel__caracteristica` with `icone--area` | `"45.00 m²"` |
| `detail_url` | Relative to absolute (`https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=547`) | Full URL string |

---

## 7. Property Detail Retrieval

Full property specifications and high-resolution galleries are retrieved via the dedicated details endpoint.

### 7.1 Detail Endpoint
```http
GET /imoveis_detalhes.php?id={property_id} HTTP/2
Host: www.imobiliariaportalmg.com.br
```

### 7.2 Structured Microdata (`Schema.org` JSON-LD)
Orangeimob embeds a `RealEstateListing` JSON-LD payload in every valid property page:
```json
{
  "@context": "https://schema.org",
  "@type": "RealEstateListing",
  "name": " em Bromélias, Timóteo",
  "url": "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608",
  "about": {
    "@type": ["House", "Product"],
    "name": "Casas -  em Bromélias, Timóteo",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Rua José Fernandes Almeida - Bromélias",
      "addressLocality": "Timóteo",
      "addressRegion": "MG",
      "postalCode": "35180512"
    },
    "map": "https://www.google.com/maps?q=Brom%C3%A9lias%2C+Tim%C3%B3teo%2C+MG",
    "amenityFeature": [
      {"@type": "LocationFeatureSpecification", "name": "Armário de cozinha"},
      {"@type": "LocationFeatureSpecification", "name": "Churrasqueira"},
      {"@type": "LocationFeatureSpecification", "name": "Closet"},
      {"@type": "LocationFeatureSpecification", "name": "Varanda"}
    ],
    "image": "https://s3.us-east-1.amazonaws.com/sgipro/703/thumb_35fca4cb7a582209e6291bf9cad2344e.jpg",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "REF",
      "value": "608"
    },
    "offers": [
      {
        "@type": "Offer",
        "priceCurrency": "BRL",
        "price": "1980.00",
        "name": "Aluguel",
        "availability": "https://schema.org/InStock",
        "businessFunction": {
          "@type": "BusinessFunction",
          "@id": "http://purl.org/goodrelations/v1#LeaseOut"
        }
      }
    ]
  }
}
```

### 7.3 Detailed Specification Badges & Pricing
In addition to JSON-LD, the HTML detail page renders extended financial and technical specifications:
- **Title**: `h1.imovel__titulo` -> e.g. `REF: 608 – Casas Bromélias – Timóteo – MG`
- **Rental Price**: `span.imovel__valor-valor` -> `R$ 1.980,00`
- **Key Specifications**: `ul.imovel__caracteristicas li`
  - `Quartos: {N}`
  - `Suítes: {N}`
  - `Banheiros: {N}`
  - `Garagens: {N}`
  - `Área útil: {N} m²`
  - `Área total: {N} m²`
  - `Condomínio: R$ {N}` (e.g. `Condomínio: R$ 260,70`)
  - `IPTU: R$ {N}`
- **Amenities List**: `div.imovel__caracteristicas2` contains itemized features marked with `√` symbols.
- **Photo Gallery**:
  - Main container: `ul.imovel__galeria`
  - Full-resolution photo links: `li.imovel__foto a.imovel__foto-link` (`href` pointing to high-resolution S3 images).
  - Thumbnail images: `ul.imovel__thumbs img.imovel__thumb-img`.

### 7.4 Non-Existent Property Handling
When querying a non-existent or deleted property ID (e.g. `id=99999`):
- HTTP Status: `200 OK`
- DOM contains an `<h1>` tag with text: `Imóvel não encontrado`
- No `imovel__titulo` or listing specification containers are present.
- The client detects this and raises a domain `PropertyNotFoundException`.

---

## 8. Verified cURL Reproduction Commands

### 8.1 Execute Target URL Search
```bash
curl -s "https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?neg=&tipo=&cidade_id=&bairro=&condominio_id=&valor=&dormitorios=1&suites=0&garagens=0&ref=&submit="
```

### 8.2 Execute Rental Search (Timóteo, Min 1 Bedroom, Price Limit R$ 2.000)
```bash
curl -s "https://www.imobiliariaportalmg.com.br/imoveis_listagem.php?neg=locacao&cidade_id=2371&dormitorios=1&valor=1-2000.00&por_pagina=10&pagina=0&ordenar=menor_valor"
```

### 8.3 Fetch Neighborhoods for Timóteo via AJAX
```bash
curl -s -X POST "https://www.imobiliariaportalmg.com.br/ajax.php?function=get_bairros_json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d "cidade_id=2371"
```

### 8.4 Fetch Property Details
```bash
curl -s "https://www.imobiliariaportalmg.com.br/imoveis_detalhes.php?id=608"
```
