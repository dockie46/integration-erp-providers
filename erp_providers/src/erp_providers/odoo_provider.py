"""Odoo ERP provider adapter."""

from __future__ import annotations

from pathlib import Path

from odoo_read import OdooClient, OdooCredentials, load_credentials
from odoo_read.auth import OdooAuthError

from .models import MaterialItem, PartnerItem, ProjectItem, UserItem, rel_id, rel_name


class OdooProvider:
    name = "odoo"

    def __init__(self, credentials: OdooCredentials) -> None:
        self._client = OdooClient.from_credentials(credentials)

    @classmethod
    def available(cls, root: Path) -> bool:
        if (root / "credentials" / "odoo.json").exists():
            return True
        try:
            load_credentials(None)
            return True
        except OdooAuthError:
            return False

    @classmethod
    def create(cls, root: Path) -> OdooProvider:
        path = root / "credentials" / "odoo.json"
        if path.exists():
            return cls(load_credentials(path))
        return cls(load_credentials(None))

    def read_users(self, limit: int | None = None) -> list[UserItem]:
        rows = self._client.get_users()
        if limit is not None:
            rows = rows[:limit]
        return [
            UserItem(
                provider=self.name,
                id=str(row["id"]),
                name=row.get("name") or "",
                email=row.get("email") or "",
                login=row.get("login") or "",
                phone=row.get("phone") or row.get("mobile") or "",
                company=rel_name(row.get("company_id")),
            )
            for row in rows
        ]

    def read_projects(self, limit: int | None = None) -> list[ProjectItem]:
        rows = self._client.get_projects()
        if limit is not None:
            rows = rows[:limit]
        return [
            ProjectItem(
                provider=self.name,
                id=str(row["id"]),
                name=row.get("name") or "",
                code=row.get("code") or "",
                partner=rel_name(row.get("partner_id")),
                analytic_account_id=rel_id(row.get("analytic_account_id")),
            )
            for row in rows
        ]

    def read_partners(self, limit: int | None = None) -> list[PartnerItem]:
        rows = self._client.get_addresses()
        if limit is not None:
            rows = rows[:limit]
        return [
            PartnerItem(
                provider=self.name,
                id=str(row["id"]),
                name=row.get("name") or "",
                email=row.get("email") or "",
                phone=row.get("phone") or row.get("mobile") or "",
                city=row.get("city") or "",
                street=row.get("street") or "",
                is_company=bool(row.get("is_company")),
            )
            for row in rows
        ]

    def read_materials(self, limit: int | None = None) -> list[MaterialItem]:
        rows = self._client.get_materials(limit=limit)
        return [_to_material(row) for row in rows]

    def search_materials(self, query: str, *, limit: int = 20) -> list[MaterialItem]:
        rows = self._client.search_materials(query, limit=limit)
        return [_to_material(row) for row in rows]


def _to_material(row: dict) -> MaterialItem:
    qty = row.get("qty_available")
    price = row.get("list_price")
    return MaterialItem(
        provider="odoo",
        id=str(row["id"]),
        name=row.get("name") or "",
        code=row.get("default_code") or "",
        barcode=row.get("barcode") or "",
        category=rel_name(row.get("categ_id")),
        uom=rel_name(row.get("uom_id")),
        list_price=float(price) if price is not None else None,
        qty_available=float(qty) if qty is not None else None,
        product_type=str(row.get("type") or ""),
    )
