"""Factory / registry over configured ERP providers."""

from __future__ import annotations

import os
from pathlib import Path

from .base import ErpProvider
from .catalog import PROVIDER_TYPES
from .models import (
    LocationItem,
    MaterialItem,
    PartnerItem,
    ProjectItem,
    StockQuantItem,
    UserItem,
)


class ErpProviders:
    """Load N ERP integrations and read master data across a subset of them.

    Example::

        p = ErpProviders.discover()
        materials = p.read_materials("odoo", limit=50)
        users = p.read_users(limit=20)
    """

    def __init__(self, providers: dict[str, ErpProvider]) -> None:
        self._providers = dict(providers)

    @classmethod
    def discover(
        cls,
        *,
        root: Path | None = None,
        providers: list[str] | tuple[str, ...] | None = None,
    ) -> ErpProviders:
        base = root or Path.cwd()
        wanted = providers
        if wanted is None:
            raw = (os.environ.get("ERP_PROVIDERS") or "").strip()
            if raw:
                wanted = tuple(part.strip() for part in raw.split(",") if part.strip())

        loaded: dict[str, ErpProvider] = {}
        for provider_type in PROVIDER_TYPES:
            if wanted is not None and provider_type.name not in wanted:
                continue
            if provider_type.available(base):
                loaded[provider_type.name] = provider_type.create(base)
        return cls(loaded)

    @property
    def names(self) -> list[str]:
        return list(self._providers)

    def get(self, name: str) -> ErpProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"Unknown provider {name!r}. Loaded: {self.names}") from exc

    def _selected(self, names: tuple[str, ...]) -> list[ErpProvider]:
        if not self._providers:
            raise RuntimeError(
                "No ERP providers loaded. Add credentials/odoo.json or ODOO_* env."
            )
        if not names:
            return list(self._providers.values())
        return [self.get(name) for name in names]

    def read_users(self, *provider_names: str, limit: int | None = 50) -> list[UserItem]:
        items: list[UserItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.read_users(limit=limit))
        return items

    def read_projects(self, *provider_names: str, limit: int | None = 50) -> list[ProjectItem]:
        items: list[ProjectItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.read_projects(limit=limit))
        return items

    def read_partners(self, *provider_names: str, limit: int | None = 50) -> list[PartnerItem]:
        items: list[PartnerItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.read_partners(limit=limit))
        return items

    def read_materials(self, *provider_names: str, limit: int | None = 50) -> list[MaterialItem]:
        items: list[MaterialItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.read_materials(limit=limit))
        return items

    def search_materials(
        self,
        query: str,
        *provider_names: str,
        limit: int = 20,
    ) -> list[MaterialItem]:
        items: list[MaterialItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.search_materials(query, limit=limit))
        return items

    def read_locations(
        self, *provider_names: str, limit: int | None = 50
    ) -> list[LocationItem]:
        items: list[LocationItem] = []
        for provider in self._selected(provider_names):
            items.extend(provider.read_locations(limit=limit))
        return items

    def read_stock_quants(
        self,
        *provider_names: str,
        location_id: str | None = None,
        product_id: str | None = None,
        limit: int | None = 50,
    ) -> list[StockQuantItem]:
        items: list[StockQuantItem] = []
        for provider in self._selected(provider_names):
            items.extend(
                provider.read_stock_quants(
                    location_id=location_id,
                    product_id=product_id,
                    limit=limit,
                )
            )
        return items
