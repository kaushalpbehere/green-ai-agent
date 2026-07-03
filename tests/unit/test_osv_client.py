import pytest
import httpx
from unittest.mock import patch, MagicMock
from src.core.sca.osv_client import OSVClient


def test_fetch_ecosystem_success():
    client = OSVClient()
    with patch("src.core.sca.osv_client.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"fake_zip_content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = client.fetch_ecosystem("PyPI")
        assert result["status"] == "success"
        assert result["ecosystem"] == "PyPI"
        assert result["url"] == f"{client.BASE_URL}/PyPI/all.zip"
        assert result["size"] == len(b"fake_zip_content")
        mock_get.assert_called_once_with(f"{client.BASE_URL}/PyPI/all.zip", timeout=30.0)


def test_fetch_ecosystem_failure():
    client = OSVClient()
    with patch("src.core.sca.osv_client.httpx.get") as mock_get:
        mock_get.side_effect = httpx.HTTPError("Network error")

        result = client.fetch_ecosystem("PyPI")
        assert result["status"] == "error"
        assert "Network error" in result["error"]
        mock_get.assert_called_once_with(f"{client.BASE_URL}/PyPI/all.zip", timeout=30.0)


def test_query_vulnerability_success():
    client = OSVClient()
    with patch("src.core.sca.osv_client.httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"vulns": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = client.query_vulnerability("jinja2", "3.1.4", "PyPI")
        assert result["status"] == "success"
        assert result["data"] == {"vulns": []}

        expected_payload = {
            "version": "3.1.4",
            "package": {
                "name": "jinja2",
                "ecosystem": "PyPI"
            }
        }
        mock_post.assert_called_once_with("https://api.osv.dev/v1/query", json=expected_payload, timeout=10.0)


def test_query_vulnerability_failure():
    client = OSVClient()
    with patch("src.core.sca.osv_client.httpx.post") as mock_post:
        mock_post.side_effect = httpx.HTTPError("Server error")

        result = client.query_vulnerability("jinja2", "3.1.4", "PyPI")
        assert result["status"] == "error"
        assert "Server error" in result["error"]
        mock_post.assert_called_once()
