"""ERP provider factory (Odoo, …)."""

from .models import (
    LocationItem,
    MaterialItem,
    PartnerItem,
    ProjectItem,
    StockQuantItem,
    UserItem,
)
from .registry import ErpProviders

__all__ = [
    "ErpProviders",
    "LocationItem",
    "MaterialItem",
    "PartnerItem",
    "ProjectItem",
    "StockQuantItem",
    "UserItem",
]

__version__ = "0.1.0"
