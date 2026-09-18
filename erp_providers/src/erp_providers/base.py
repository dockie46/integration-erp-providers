"""ERP provider protocol and discovery hooks."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import MaterialItem, PartnerItem, ProjectItem, UserItem


class ErpProvider(Protocol):
    @property
    def name(self) -> str: ...

    def read_users(self, limit: int | None = None) -> list[UserItem]: ...

    def read_projects(self, limit: int | None = None) -> list[ProjectItem]: ...

    def read_partners(self, limit: int | None = None) -> list[PartnerItem]: ...

    def read_materials(self, limit: int | None = None) -> list[MaterialItem]: ...

    def search_materials(self, query: str, *, limit: int = 20) -> list[MaterialItem]: ...


class ErpProviderType(Protocol):
    name: str

    @classmethod
    def available(cls, root: Path) -> bool: ...

    @classmethod
    def create(cls, root: Path) -> ErpProvider: ...
