"""ERP provider factory (Odoo, …)."""

from .models import MaterialItem, PartnerItem, ProjectItem, UserItem
from .registry import ErpProviders

__all__ = [
    "ErpProviders",
    "MaterialItem",
    "PartnerItem",
    "ProjectItem",
    "UserItem",
]

__version__ = "0.1.0"
