"""Odoo connection credentials (file or environment)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


class OdooAuthError(RuntimeError):
    """Raised when Odoo authentication fails."""


@dataclass(frozen=True, slots=True)
class OdooCredentials:
    url: str
    db: str
    login: str
    password: str
    http_user: str = ""
    http_password: str = ""


def load_credentials(path: Path | None = None) -> OdooCredentials:
    """Load from credentials/odoo.json or ODOO_* environment variables."""
    if path is not None and path.exists():
        data = json.loads(path.read_text())
        return OdooCredentials(
            url=(data.get("url") or "").strip(),
            db=(data.get("db") or "").strip(),
            login=(data.get("login") or "").strip(),
            password=(data.get("password") or "").strip(),
            http_user=(data.get("http_user") or "").strip(),
            http_password=(data.get("http_password") or "").strip(),
        )

    creds = OdooCredentials(
        url=(os.environ.get("ODOO_URL") or "").strip(),
        db=(os.environ.get("ODOO_DB") or "").strip(),
        login=(os.environ.get("ODOO_LOGIN") or "").strip(),
        password=(os.environ.get("ODOO_PASSWORD") or "").strip(),
        http_user=(os.environ.get("ODOO_HTTP_USER") or "").strip(),
        http_password=(os.environ.get("ODOO_HTTP_PASSWORD") or "").strip(),
    )
    if not (creds.url and creds.db and creds.login and creds.password):
        raise OdooAuthError(
            "Odoo credentials missing.\n"
            "Set credentials/odoo.json or env ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD."
        )
    return creds
