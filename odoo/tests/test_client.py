"""Unit tests for OdooClient (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from odoo_read import OdooAuthError, OdooClient, OdooCredentials


@pytest.fixture
def creds() -> OdooCredentials:
    return OdooCredentials(
        url="https://odoo.example.com",
        db="testdb",
        login="sync@example.com",
        password="secret",
    )


@patch("odoo_read.client.requests.Session")
def test_authenticate_success(mock_session_cls, creds):
    mock_session = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": {"uid": 42}}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    client = OdooClient(creds)
    client.authenticate()
    assert client._uid == 42
    assert "/web/session/authenticate" in mock_session.post.call_args[0][0]


@patch("odoo_read.client.requests.Session")
def test_authenticate_failure(mock_session_cls, creds):
    mock_session = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": {"uid": False}, "error": {"message": "bad"}}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    client = OdooClient(creds)
    with pytest.raises(OdooAuthError):
        client.authenticate()


@patch("odoo_read.client.requests.Session")
def test_get_materials(mock_session_cls, creds):
    mock_session = MagicMock()
    mock_session_cls.return_value = mock_session

    auth = MagicMock()
    auth.json.return_value = {"result": {"uid": 1}}
    auth.raise_for_status.return_value = None

    materials = MagicMock()
    materials.json.return_value = {
        "result": [
            {
                "id": 7,
                "name": "Cement",
                "default_code": "CEM-01",
                "categ_id": [3, "Building"],
                "uom_id": [1, "kg"],
                "list_price": 12.5,
                "qty_available": 100.0,
                "type": "product",
            }
        ]
    }
    materials.raise_for_status.return_value = None
    mock_session.post.side_effect = [auth, materials]

    client = OdooClient(creds)
    rows = client.get_materials(limit=10)
    assert rows[0]["default_code"] == "CEM-01"
    assert "/web/dataset/call_kw" in mock_session.post.call_args_list[1][0][0]
