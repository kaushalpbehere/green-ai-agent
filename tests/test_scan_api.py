"""
Tests for the scan and project management API endpoints
"""

import pytest
import json
from src.ui.server import app, project_manager


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def cleanup():
    """Clean up before and after tests"""
    # Clean up before test
    for project_name in list(project_manager.projects.keys()):
        if project_name.startswith('test_'):
            try:
                project_manager.remove_project(project_name)
            except:
                pass
    
    yield
    
    # Clean up after test
    for project_name in list(project_manager.projects.keys()):
        if project_name.startswith('test_'):
            try:
                project_manager.remove_project(project_name)
            except:
                pass


class TestScanAPI:
    """Tests for POST /api/scan endpoint"""
    
    def test_scan_with_git_url(self, client, cleanup):
        """Test creating a new scan with Git URL"""
        data = {
            'project_name': 'test_git_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git'
        }
        response = client.post('/api/scan', 
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert result['project_name'] == 'test_git_project'
        assert result['scan_type'] == 'git'
    
    def test_scan_with_local_path(self, client, cleanup):
        """Test creating a new scan with local path"""
        data = {
            'project_name': 'test_local_project',
            'language': 'javascript',
            'path': '/path/to/code'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert result['scan_type'] == 'local'
    
    def test_scan_missing_project_name(self, client):
        """Test scan fails without project name"""
        data = {
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_scan_missing_language(self, client):
        """Test scan fails without language"""
        data = {
            'project_name': 'test_project',
            'git_url': 'https://github.com/example/repo.git'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_scan_with_branch(self, client, cleanup):
        """Test scan with Git branch specification"""
        data = {
            'project_name': 'test_branch_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git@main'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['project_name'] == 'test_branch_project'


class TestProjectDeletion:
    """Tests for DELETE /api/projects/<name> endpoint"""
    
    def test_delete_existing_project(self, client, cleanup):
        """Test deleting an existing project"""
        # First create a project
        project_manager.add_project('test_delete_project', 'python', 
                                   'https://github.com/example/repo.git', 'auto')
        
        # Then delete it
        response = client.delete('/api/projects/test_delete_project')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert 'deleted' in result['message'].lower()
    
    def test_delete_nonexistent_project(self, client):
        """Test deleting a project that doesn't exist"""
        response = client.delete('/api/projects/nonexistent_project')
        
        # Should still return 200 (graceful deletion)
        assert response.status_code == 200


class TestProjectRescan:
    """Tests for POST /api/projects/<name>/rescan endpoint"""
    
    def test_rescan_existing_project(self, client, cleanup):
        """Test rescanning an existing project"""
        # Create a project first
        project_manager.add_project('test_rescan_project', 'python',
                                   'https://github.com/example/repo.git', 'auto')
        
        # Rescan it
        response = client.post('/api/projects/test_rescan_project/rescan')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert 'rescan' in result['message'].lower()
    
    def test_rescan_nonexistent_project(self, client):
        """Test rescanning a project that doesn't exist"""
        response = client.post('/api/projects/nonexistent_project/rescan')
        
        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result


class TestProjectClear:
    """Tests for POST /api/projects/<name>/clear endpoint"""
    
    def test_clear_existing_project(self, client, cleanup):
        """Test clearing violations from a project"""
        # Create a project with violations
        project_manager.add_project('test_clear_project', 'python',
                                   'https://github.com/example/repo.git', 'auto')
        project = project_manager.get_project('test_clear_project')
        project['violations'] = [{'severity': 'critical', 'message': 'Test violation'}]
        project['scanning_emissions'] = 0.0001
        project['codebase_emissions'] = 0.0002
        
        # Clear it
        response = client.post('/api/projects/test_clear_project/clear')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        
        # Verify violations are cleared
        project = project_manager.get_project('test_clear_project')
        assert project['violations'] == []
        assert project['scanning_emissions'] == 0
        assert project['codebase_emissions'] == 0
    
    def test_clear_nonexistent_project(self, client):
        """Test clearing a project that doesn't exist"""
        response = client.post('/api/projects/nonexistent_project/clear')
        
        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result


class TestProjectEndpointIntegration:
    """Integration tests for full project lifecycle"""
    
    def test_full_project_lifecycle(self, client, cleanup):
        """Test creating, rescanning, and deleting a project"""
        # Create
        scan_data = {
            'project_name': 'test_lifecycle_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git'
        }
        response = client.post('/api/scan',
                              data=json.dumps(scan_data),
                              content_type='application/json')
        assert response.status_code == 200
        
        # Rescan
        response = client.post('/api/projects/test_lifecycle_project/rescan')
        assert response.status_code == 200
        
        # Clear
        response = client.post('/api/projects/test_lifecycle_project/clear')
        assert response.status_code == 200
        
        # Delete
        response = client.delete('/api/projects/test_lifecycle_project')
        assert response.status_code == 200


class TestAPIErrorHandling:
    """Tests for API error handling and edge cases"""
    
    def test_scan_with_special_characters_in_name(self, client, cleanup):
        """Test scan with special characters in project name"""
        data = {
            'project_name': 'test-project_v1.0',
            'language': 'python',
            'path': '/path/to/code'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
    
    def test_delete_with_url_encoding(self, client, cleanup):
        """Test delete with URL-encoded project name"""
        # Create project with special name
        project_manager.add_project('test project with spaces', 'python',
                                   'https://github.com/example/repo.git', 'auto')
        
        # Delete with URL encoding
        response = client.delete('/api/projects/test%20project%20with%20spaces')
        
        assert response.status_code == 200
    
    def test_malformed_json_request(self, client):
        """Test API handles malformed JSON gracefully"""
        response = client.post('/api/scan',
                              data='invalid json',
                              content_type='application/json')
        
        # Should handle gracefully or return 400
        assert response.status_code in [400, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
