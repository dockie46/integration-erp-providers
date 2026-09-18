"""Demo: read Odoo materials / users via ErpProviders."""

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

    print(f"Loaded: {', '.join(providers.names)}")
    print()
    print("=== Materials (first 10) ===")
    for i, item in enumerate(providers.read_materials(limit=10), start=1):
        code = item.code or "-"
        print(f"{i:2}. [{item.provider}] {code}  {item.name}  uom={item.uom or '-'}  qty={item.qty_available}")

    print()
    print("=== Users (first 5) ===")
    for i, item in enumerate(providers.read_users(limit=5), start=1):
        print(f"{i:2}. [{item.provider}] {item.name}  {item.email or item.login}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
