# integration-erp-providers

Public ERP integration library — **Odoo** first, more providers later.

Same pattern as [integration-tools](https://github.com/dockie46/integration-tools) (communication),
but for ERP master data.

```sh
make init
uv run python main.py
make test
```

```
integration-erp-providers/
  odoo/              # JSON-RPC client (odoo-read)
  erp_providers/     # ErpProviders factory
  credentials/       # secrets — never commit
  main.py
```

## API

```python
from erp_providers import ErpProviders

p = ErpProviders.discover()
materials = p.read_materials("odoo", limit=50)
materials = p.search_materials("cement", "odoo", limit=20)
locations = p.read_locations(limit=20)
stock = p.read_stock_quants(location_id="15", limit=50)
users = p.read_users(limit=20)
projects = p.read_projects(limit=20)
partners = p.read_partners(limit=20)
```

## Credentials

`credentials/odoo.json` (gitignored):

```json
{
  "url": "https://odoo.example.com",
  "db": "mydb",
  "login": "api@example.com",
  "password": "…",
  "http_user": "",
  "http_password": ""
}
```

Or env: `ODOO_URL`, `ODOO_DB`, `ODOO_LOGIN`, `ODOO_PASSWORD`
(+ optional `ODOO_HTTP_USER` / `ODOO_HTTP_PASSWORD`).

## Materials

Read from Odoo `product.product` (active variants): code, barcode, category, UoM.
Stock qty on the product is opt-in (slow); prefer `read_stock_quants` for location-aware qty.

## Locations & stock (e-ink ready)

- `read_locations` → Odoo `stock.location` (default `usage=internal`)
- `read_stock_quants` → Odoo `stock.quant` (product × location × quantity)

Based on the Odoo client used in Construction Diary Log, plus product/material and stock reads.


