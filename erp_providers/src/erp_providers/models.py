"""Unified provider models for ERP master data."""

from __future__ import annotations

from dataclasses import asdict, dataclass


def _rel_id(field) -> int | None:
    if isinstance(field, (list, tuple)) and field:
        return int(field[0])
    if isinstance(field, int):
        return field
    return None


def _rel_name(field) -> str:
    if isinstance(field, (list, tuple)) and len(field) >= 2:
        return str(field[1] or "")
    return ""


@dataclass(frozen=True, slots=True)
class UserItem:
    provider: str
    id: str
    name: str
    email: str = ""
    login: str = ""
    phone: str = ""
    company: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProjectItem:
    provider: str
    id: str
    name: str
    code: str = ""
    partner: str = ""
    analytic_account_id: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PartnerItem:
    provider: str
    id: str
    name: str
    email: str = ""
    phone: str = ""
    city: str = ""
    street: str = ""
    is_company: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MaterialItem:
    """Product / material (Odoo ``product.product``)."""

    provider: str
    id: str
    name: str
    code: str = ""
    barcode: str = ""
    category: str = ""
    uom: str = ""
    list_price: float | None = None
    qty_available: float | None = None
    product_type: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# Re-export helpers for adapters
rel_id = _rel_id
rel_name = _rel_name
