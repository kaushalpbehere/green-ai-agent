"""
Tests for Dashboard API Responses and Error Handling
"""

import pytest
import json
from unittest.mock import patch, mock_open
from src.ui.dashboard_app import app, load_template
import src.ui.dashboard_app as dashboard_app_module

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestDashboardResponses:
    """Test dashboard API responses for correctness"""

    def test_api_charts_content_type(self, client):
        """Test that api_charts returns application/json"""
        with patch('src.ui.dashboard_app.last_charts', {'data': [1, 2, 3]}):
            response = client.get('/api/charts')
            assert response.content_type == 'application/json'

    def test_api_results_content_type(self, client):
        """Test that api_results returns application/json"""
        with patch('src.ui.dashboard_app.last_scan_results', {'issues': []}):
            response = client.get('/api/results')
            assert response.content_type == 'application/json'

class TestTemplateLoading:
    """Test template loading error handling"""

    def setup_method(self):
        # Reset cached templates before test
        dashboard_app_module.LANDING_PAGE_HTML = None
        dashboard_app_module.DASHBOARD_HTML = None

    def teardown_method(self):
        # Reset cached templates after test
        dashboard_app_module.LANDING_PAGE_HTML = None
        dashboard_app_module.DASHBOARD_HTML = None

    def test_load_template_missing_file(self):
        """Test load_template handles missing files gracefully"""
        with patch('builtins.open', side_effect=FileNotFoundError("Template not found")):
            result = load_template('missing.html')
            assert "Error: Template missing.html could not be loaded" in result

    def test_dashboard_route_missing_template(self, client):
        """Test dashboard route when template is missing"""
        # Patch open only within this context
        with patch('builtins.open', side_effect=FileNotFoundError("Template not found")):
             # Ensure we force a reload by clearing cache again just in case
             dashboard_app_module.LANDING_PAGE_HTML = None
             response = client.get('/')
             assert response.status_code != 500
             assert b"Error" in response.data or b"Template" in response.data
