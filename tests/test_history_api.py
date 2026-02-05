"""
Tests for History API Endpoints
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Flask test client"""
    from src.ui.server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_history_dir(tmp_path):
    """Create temporary history directory"""
    history_dir = tmp_path / "history"
    history_dir.mkdir()
    
    original_home = Path.home()
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    
    with patch('pathlib.Path.home', return_value=mock_home):
        yield history_dir


class TestHistoryAPI:
    """Test history API endpoints"""
    
    def test_api_history_missing_project(self, client):
        """Test /api/history without project parameter"""
        response = client.get('/api/history')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'project' in data['error'].lower()
    
    def test_api_history_empty(self, client):
        """Test /api/history with no scans"""
        response = client.get('/api/history?project=empty-project')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['project'] == 'empty-project'
        assert data['count'] == 0
        assert data['scans'] == []
    
    def test_api_trending_missing_project(self, client):
        """Test /api/trending without project parameter"""
        response = client.get('/api/trending')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_trending_no_scans(self, client):
        """Test /api/trending with no history"""
        response = client.get('/api/trending?project=new-project')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['project'] == 'new-project'
        assert data['trend'] == 'insufficient_data'
    
    def test_api_compare_missing_project(self, client):
        """Test /api/compare without project parameter"""
        response = client.get('/api/compare')
        assert response.status_code == 400
    
    def test_api_compare_insufficient_scans(self, client):
        """Test /api/compare with fewer than 2 scans"""
        response = client.get('/api/compare?project=single-scan-project')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Not enough scans' in data['error']
    
    def test_api_history_invalid_project_name(self, client):
        """Test API with special characters in project name"""
        response = client.get('/api/history?project=my%20project%20name')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'project' in data
    
    def test_api_endpoints_return_json(self, client):
        """Test that all history endpoints return valid JSON"""
        # Test history endpoint
        response = client.get('/api/history?project=test')
        assert response.content_type == 'application/json'
        
        # Test trending endpoint
        response = client.get('/api/trending?project=test')
        assert response.content_type == 'application/json'
        
        # Test compare endpoint (will fail due to insufficient scans, but should return JSON)
        response = client.get('/api/compare?project=test')
        assert response.content_type == 'application/json'
