"""Odoo JSON-RPC 2.0 HTTP client.

Extracted/adapted from ConstructionDiaryLog work_diary.services.odooclient,
plus product/material reads for ERP master data.
"""

from __future__ import annotations

import requests

from .auth import OdooAuthError, OdooCredentials, load_credentials


class OdooClient:
    def __init__(self, credentials: OdooCredentials) -> None:
        self._credentials = credentials
        self._url = credentials.url.rstrip("/")
        self._session = requests.Session()
        if credentials.http_user:
            self._session.auth = (credentials.http_user, credentials.http_password)
        self._uid: int | None = None

    @classmethod
    def from_credentials(cls, credentials: OdooCredentials) -> OdooClient:
        return cls(credentials)

    @classmethod
    def from_file(cls, path) -> OdooClient:
        return cls(load_credentials(path))

    @classmethod
    def from_env(cls) -> OdooClient:
        return cls(load_credentials(None))

    def authenticate(self) -> None:
        """Authenticate to Odoo and store session cookie."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self._credentials.db,
                "login": self._credentials.login,
                "password": self._credentials.password,
            },
        }
        resp = self._session.post(f"{self._url}/web/session/authenticate", json=payload)
        resp.raise_for_status()
        result = resp.json().get("result", {})
        uid = result.get("uid")
        if not uid:
            raise OdooAuthError(
                f"Odoo authentication failed for {self._credentials.login}: "
                f"{resp.json().get('error', {}).get('message', 'unknown error')}"
            )
        self._uid = uid

    def ensure_authenticated(self) -> None:
        if self._uid is None:
            self.authenticate()

    def _call_kw(
        self,
        model: str,
        method: str,
        args: list,
        kwargs: dict | None = None,
    ) -> list | dict | bool | int:
        """Execute a JSON-RPC call_kw request."""
        self.ensure_authenticated()
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs or {},
            },
        }
        resp = self._session.post(f"{self._url}/web/dataset/call_kw", json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(
                f"Odoo RPC error on {model}.{method}: {data['error'].get('message', 'unknown')}"
            )
        return data.get("result", [])

    # --- users ---

    def get_users(self) -> list[dict]:
        return self._call_kw(
            model="res.users",
            method="search_read",
            args=[[["active", "=", True]]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "login",
                    "email",
                    "phone",
                    "mobile",
                    "job_title",
                    "company_id",
                    "department_id",
                ],
            },
        )

    def get_user(self, user_id: int) -> dict | None:
        results = self._call_kw(
            model="res.users",
            method="read",
            args=[[user_id]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "login",
                    "email",
                    "phone",
                    "mobile",
                    "job_title",
                    "company_id",
                    "department_id",
                ],
            },
        )
        return results[0] if results else None

    def search_users(self, query: str, *, limit: int = 20) -> list[dict]:
        return self._call_kw(
            model="res.users",
            method="search_read",
            args=[
                [
                    "&",
                    ["active", "=", True],
                    "|",
                    "|",
                    ["name", "ilike", query],
                    ["email", "ilike", query],
                    ["login", "ilike", query],
                ]
            ],
            kwargs={"fields": ["id", "name", "login", "email"], "limit": limit},
        )

    # --- projects ---

    def get_projects(self) -> list[dict]:
        return self._call_kw(
            model="project.project",
            method="search_read",
            args=[[["analytic_account_id", "!=", False]]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "code",
                    "analytic_account_id",
                    "partner_id",
                    "date_start",
                    "date",
                    "user_id",
                    "description",
                    "active",
                    "task_count",
                    "company_id",
                ],
            },
        )

    def get_project(self, project_id: int) -> dict | None:
        results = self._call_kw(
            model="project.project",
            method="read",
            args=[[project_id]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "code",
                    "analytic_account_id",
                    "partner_id",
                    "date_start",
                    "date",
                    "user_id",
                    "description",
                    "active",
                    "task_count",
                    "company_id",
                ],
            },
        )
        return results[0] if results else None

    def search_projects(self, query: str, *, limit: int = 20) -> list[dict]:
        return self._call_kw(
            model="project.project",
            method="search_read",
            args=[
                [
                    "|",
                    "|",
                    ["name", "ilike", query],
                    ["code", "ilike", query],
                    ["analytic_account_id.name", "ilike", query],
                ]
            ],
            kwargs={
                "fields": ["id", "name", "code", "analytic_account_id"],
                "limit": limit,
            },
        )

    # --- partners / addresses ---

    def get_partner(self, partner_id: int) -> dict | None:
        results = self._call_kw(
            model="res.partner",
            method="read",
            args=[[partner_id]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "street",
                    "city",
                    "zip",
                    "country_id",
                    "email",
                    "phone",
                    "type",
                ],
            },
        )
        return results[0] if results else None

    def get_addresses(self) -> list[dict]:
        return self._call_kw(
            model="res.partner",
            method="search_read",
            args=[[["active", "=", True]]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "is_company",
                    "street",
                    "street2",
                    "city",
                    "zip",
                    "state_id",
                    "country_id",
                    "email",
                    "phone",
                    "mobile",
                    "type",
                    "vat",
                    "website",
                    "company_name",
                    "parent_id",
                    "commercial_partner_id",
                ],
            },
        )

    def search_contacts(self, query: str, *, limit: int = 20) -> list[dict]:
        return self._call_kw(
            model="res.partner",
            method="search_read",
            args=[
                [
                    "&",
                    "&",
                    ["active", "=", True],
                    ["is_company", "=", False],
                    "|",
                    ["name", "ilike", query],
                    ["email", "ilike", query],
                ]
            ],
            kwargs={
                "fields": ["id", "name", "email", "phone", "mobile", "parent_id"],
                "limit": limit,
            },
        )

    def search_addresses(self, query: str, *, limit: int = 20) -> list[dict]:
        return self._call_kw(
            model="res.partner",
            method="search_read",
            args=[
                [
                    "&",
                    ["active", "=", True],
                    "|",
                    "|",
                    ["name", "ilike", query],
                    ["city", "ilike", query],
                    ["street", "ilike", query],
                ]
            ],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "street",
                    "city",
                    "zip",
                    "country_id",
                    "email",
                    "phone",
                    "type",
                ],
                "limit": limit,
            },
        )

    # --- materials / products ---

    def get_materials(self, *, limit: int | None = None) -> list[dict]:
        """Fetch active product variants (materials) from Odoo ``product.product``."""
        kwargs: dict = {
            "fields": [
                "id",
                "name",
                "default_code",
                "barcode",
                "categ_id",
                "uom_id",
                "uom_po_id",
                "list_price",
                "standard_price",
                "type",
                "qty_available",
                "virtual_available",
                "active",
                "product_tmpl_id",
                "description_sale",
            ],
            "order": "default_code, name",
        }
        if limit is not None:
            kwargs["limit"] = limit
        return self._call_kw(
            model="product.product",
            method="search_read",
            args=[[["active", "=", True]]],
            kwargs=kwargs,
        )

    def get_material(self, product_id: int) -> dict | None:
        results = self._call_kw(
            model="product.product",
            method="read",
            args=[[product_id]],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "default_code",
                    "barcode",
                    "categ_id",
                    "uom_id",
                    "uom_po_id",
                    "list_price",
                    "standard_price",
                    "type",
                    "qty_available",
                    "virtual_available",
                    "active",
                    "product_tmpl_id",
                    "description_sale",
                ],
            },
        )
        return results[0] if results else None

    def search_materials(self, query: str, *, limit: int = 20) -> list[dict]:
        """Search materials by name, internal reference, or barcode."""
        return self._call_kw(
            model="product.product",
            method="search_read",
            args=[
                [
                    "&",
                    ["active", "=", True],
                    "|",
                    "|",
                    ["name", "ilike", query],
                    ["default_code", "ilike", query],
                    ["barcode", "ilike", query],
                ]
            ],
            kwargs={
                "fields": [
                    "id",
                    "name",
                    "default_code",
                    "barcode",
                    "categ_id",
                    "uom_id",
                    "list_price",
                    "type",
                    "qty_available",
                ],
                "limit": limit,
            },
        )

    def get_material_categories(self) -> list[dict]:
        return self._call_kw(
            model="product.category",
            method="search_read",
            args=[[]],
            kwargs={"fields": ["id", "name", "complete_name", "parent_id"]},
        )
