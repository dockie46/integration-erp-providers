"""Unit tests for ErpProviders factory."""

from __future__ import annotations

from erp_providers.models import (
    LocationItem,
    MaterialItem,
    PartnerItem,
    ProjectItem,
    StockQuantItem,
    UserItem,
)
from erp_providers.registry import ErpProviders


class _FakeOdoo:
    name = "odoo"

    def read_users(self, limit: int | None = None) -> list[UserItem]:
        items = [UserItem(provider="odoo", id="1", name="Alice", email="a@x.com")]
        return items[:limit] if limit is not None else items

    def read_projects(self, limit: int | None = None) -> list[ProjectItem]:
        items = [ProjectItem(provider="odoo", id="10", name="Site A", code="PRJ-1")]
        return items[:limit] if limit is not None else items

    def read_partners(self, limit: int | None = None) -> list[PartnerItem]:
        items = [PartnerItem(provider="odoo", id="2", name="ACME", is_company=True)]
        return items[:limit] if limit is not None else items

    def read_materials(self, limit: int | None = None) -> list[MaterialItem]:
        items = [
            MaterialItem(provider="odoo", id="7", name="Cement", code="CEM-01", uom="kg"),
            MaterialItem(provider="odoo", id="8", name="Sand", code="SND-01", uom="t"),
        ]
        return items[:limit] if limit is not None else items

    def search_materials(self, query: str, *, limit: int = 20) -> list[MaterialItem]:
        return [m for m in self.read_materials() if query.lower() in m.name.lower()][:limit]

    def read_locations(self, limit: int | None = None) -> list[LocationItem]:
        items = [
            LocationItem(
                provider="odoo",
                id="15",
                name="Stock",
                complete_name="Physical Locations/CBSS/Sklad",
                usage="internal",
            )
        ]
        return items[:limit] if limit is not None else items

    def read_stock_quants(
        self,
        *,
        location_id: str | None = None,
        product_id: str | None = None,
        limit: int | None = None,
    ) -> list[StockQuantItem]:
        items = [
            StockQuantItem(
                provider="odoo",
                id="49",
                product_id="228",
                product_name="Board",
                location_id="15",
                location_name="CBSS/Sklad",
                quantity=12.0,
            )
        ]
        if location_id is not None:
            items = [q for q in items if q.location_id == location_id]
        if product_id is not None:
            items = [q for q in items if q.product_id == product_id]
        return items[:limit] if limit is not None else items


def test_read_materials() -> None:
    p = ErpProviders({"odoo": _FakeOdoo()})
    items = p.read_materials("odoo", limit=1)
    assert len(items) == 1
    assert items[0].code == "CEM-01"


def test_search_materials() -> None:
    p = ErpProviders({"odoo": _FakeOdoo()})
    items = p.search_materials("sand", "odoo")
    assert items[0].name == "Sand"


def test_read_locations_and_stock() -> None:
    p = ErpProviders({"odoo": _FakeOdoo()})
    locs = p.read_locations("odoo")
    assert locs[0].id == "15"
    quants = p.read_stock_quants("odoo", location_id="15")
    assert quants[0].quantity == 12.0
