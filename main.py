"""Demo: read Odoo materials, locations, stock via ErpProviders."""

from __future__ import annotations

import sys
from pathlib import Path

from erp_providers import ErpProviders

ROOT = Path(__file__).resolve().parent


def main() -> int:
    providers = ErpProviders.discover(root=ROOT)
    if not providers.names:
        print(
            "No ERP providers. Add credentials/odoo.json or set ODOO_URL/DB/LOGIN/PASSWORD.",
            file=sys.stderr,
        )
        return 1

    print(f"Loaded: {', '.join(providers.names)}", flush=True)
    print(flush=True)
    print("=== Materials (first 10) ===", flush=True)
    print("(fetching from Odoo…)", flush=True)
    for i, item in enumerate(providers.read_materials(limit=10), start=1):
        code = item.code or "-"
        print(
            f"{i:2}. [{item.provider}] {code}  {item.name}  uom={item.uom or '-'}",
            flush=True,
        )

    print(flush=True)
    print("=== Locations (internal) ===", flush=True)
    print("(fetching from Odoo…)", flush=True)
    locations = providers.read_locations(limit=20)
    for i, loc in enumerate(locations, start=1):
        print(f"{i:2}. [{loc.provider}] {loc.id}  {loc.complete_name or loc.name}", flush=True)

    print(flush=True)
    print("=== Stock quants (first 10, qty>0) ===", flush=True)
    print("(fetching from Odoo…)", flush=True)
    for i, q in enumerate(providers.read_stock_quants(limit=10), start=1):
        print(
            f"{i:2}. [{q.provider}] qty={q.quantity:g}  {q.product_name}  @ {q.location_name}",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
