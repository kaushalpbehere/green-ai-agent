from fastapi.testclient import TestClient
from unittest.mock import patch

from src.ui.app_fastapi import app


client = TestClient(app)


def test_api_disable_rule():
    # We mock the state.get_standards_registry().disable_rule call
    with patch("src.ui.app_fastapi.state.get_standards_registry") as mock_get_registry:
        mock_registry = mock_get_registry.return_value
        mock_registry.disable_rule.return_value = None

        response = client.post("/api/rules/test_rule_123/disable")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "Rule test_rule_123 disabled"}
        mock_registry.disable_rule.assert_called_once_with("test_rule_123")
