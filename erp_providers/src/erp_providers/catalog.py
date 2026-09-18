"""Known ERP provider types — add one line for a new integration."""

from __future__ import annotations

from .base import ErpProviderType
from .odoo_provider import OdooProvider

PROVIDER_TYPES: tuple[type[ErpProviderType], ...] = (
    OdooProvider,
)
