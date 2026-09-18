"""Unit tests for ErpProviders factory."""

from __future__ import annotations

from erp_providers.models import MaterialItem, PartnerItem, ProjectItem, UserItem
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


def test_read_materials() -> None:
    p = ErpProviders({"odoo": _FakeOdoo()})
    items = p.read_materials("odoo", limit=1)
    assert len(items) == 1
    assert items[0].code == "CEM-01"


def test_search_materials() -> None:
    p = ErpProviders({"odoo": _FakeOdoo()})
    items = p.search_materials("sand", "odoo")
    assert items[0].name == "Sand"
