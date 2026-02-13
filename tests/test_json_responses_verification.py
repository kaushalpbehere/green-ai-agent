import pytest
import json
from unittest.mock import patch
from src.ui.dashboard_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestJsonResponsesVerification:
    """Explicit verification for api_charts and api_results"""

    def test_api_charts_with_data(self, client):
        """Verify api_charts returns correct JSON structure and content type"""
        mock_charts = {'severity_chart': {'data': [1, 2, 3]}}
        with patch('src.ui.dashboard_app.last_charts', mock_charts):
            response = client.get('/api/charts')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.get_json() == mock_charts

    def test_api_charts_empty(self, client):
        """Verify api_charts returns empty JSON object when no data"""
        with patch('src.ui.dashboard_app.last_charts', None):
            response = client.get('/api/charts')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.get_json() == {}

    def test_api_results_with_data(self, client):
        """Verify api_results returns correct JSON structure and content type"""
        mock_results = {'issues': [{'id': 'test', 'severity': 'high'}], 'emissions': 0.5}
        with patch('src.ui.dashboard_app.last_scan_results', mock_results):
            response = client.get('/api/results')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.get_json() == mock_results

    def test_api_results_empty(self, client):
        """Verify api_results returns empty JSON object when no data"""
        with patch('src.ui.dashboard_app.last_scan_results', None):
            response = client.get('/api/results')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.get_json() == {}
