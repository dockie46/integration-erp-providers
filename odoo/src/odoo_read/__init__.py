"""Odoo JSON-RPC client for ERP integrations."""

from .auth import OdooAuthError, OdooCredentials, load_credentials
from .client import OdooClient

__all__ = [
    "OdooAuthError",
    "OdooClient",
    "OdooCredentials",
    "load_credentials",
]

__version__ = "0.1.0"
