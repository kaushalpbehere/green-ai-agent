"""
Tests for the scan and project management API endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.ui.dashboard_app import app
from src.core.project_manager import ProjectManager


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_project_manager(tmp_path):
    """
    Create a ProjectManager instance with temporary storage
    and patch the server to use it.
    """
    # Patch the CONFIG_DIR and REGISTRY_FILE on the class
    # Note: ProjectManager defines these as class attributes based on Path.home() at module level.
    # So we need to patch them where they are defined.

    test_config_dir = tmp_path / '.green-ai'
    test_registry_file = test_config_dir / 'projects.json'
    test_history_dir = test_config_dir / 'history'

    with patch('src.core.project_manager.ProjectManager.CONFIG_DIR', test_config_dir), \
         patch('src.core.project_manager.ProjectManager.REGISTRY_FILE', test_registry_file), \
         patch('src.core.project_manager.ProjectManager.HISTORY_DIR', test_history_dir):

        # Instantiate PM
        pm = ProjectManager()
        # Ensure directories exist (ProjectManager.__init__ does this, but we want to be sure with our patched paths)
        # Actually ProjectManager.__init__ uses self.CONFIG_DIR which should be patched.

        # Patch the server's getter
        with patch('src.ui.dashboard_app.get_project_manager', return_value=pm):
            yield pm


@pytest.fixture
def cleanup(mock_project_manager):
    """Clean up before and after tests"""
    pm = mock_project_manager
    # Clean up before test
    for project in list(pm.projects.values()):
        if project.name.startswith('test_'):
            try:
                pm.remove_project(project.name)
            except:
                pass
    
    yield
    
    # Clean up after test
    for project in list(pm.projects.values()):
        if project.name.startswith('test_'):
            try:
                pm.remove_project(project.name)
            except:
                pass


class TestScanAPI:
    """Tests for POST /api/scan endpoint"""
    
    def test_scan_with_git_url(self, client, cleanup, mock_project_manager):
        """Test creating a new scan with Git URL"""
        data = {
            'project_name': 'test_git_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git'
        }
        
        # We need to mock background scan execution to avoid actual git operations/scanning
        with patch('src.ui.dashboard_app.Scanner'), \
             patch('src.ui.dashboard_app.threading.Thread'):

            response = client.post('/api/scan',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'ok'
            assert result['project_name'] == 'test_git_project'
            assert result['scan_type'] == 'git'

            # Verify project was added
            assert mock_project_manager.get_project('test_git_project') is not None
    
    def test_scan_with_local_path(self, client, cleanup, mock_project_manager):
        """Test creating a new scan with local path"""
        data = {
            'project_name': 'test_local_project',
            'language': 'javascript',
            'path': '/path/to/code'
        }
        
        with patch('src.ui.dashboard_app.Scanner'), \
             patch('src.ui.dashboard_app.threading.Thread'):

            response = client.post('/api/scan',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'ok'
            assert result['scan_type'] == 'local'

            assert mock_project_manager.get_project('test_local_project') is not None
    
    def test_scan_missing_project_name(self, client, mock_project_manager):
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
    
    def test_scan_missing_language(self, client, mock_project_manager):
        """Test scan fails without language"""
        data = {
            'project_name': 'test_project',
            'git_url': 'https://github.com/example/repo.git'
        }
        response = client.post('/api/scan',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_scan_with_branch(self, client, cleanup, mock_project_manager):
        """Test scan with Git branch specification"""
        data = {
            'project_name': 'test_branch_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git@main'
        }
        
        with patch('src.ui.dashboard_app.Scanner'), \
             patch('src.ui.dashboard_app.threading.Thread'):

            response = client.post('/api/scan',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['project_name'] == 'test_branch_project'


class TestProjectDeletion:
    """Tests for DELETE /api/projects/<name> endpoint"""
    
    def test_delete_existing_project(self, client, cleanup, mock_project_manager):
        """Test deleting an existing project"""
        # First create a project
        mock_project_manager.add_project('test_delete_project', 'https://github.com/example/repo.git', 'main', 'python')
        
        # Then delete it
        response = client.delete('/api/projects/test_delete_project')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert 'deleted' in result['message'].lower()

        assert mock_project_manager.get_project('test_delete_project') is None
    
    def test_delete_nonexistent_project(self, client, mock_project_manager):
        """Test deleting a project that doesn't exist"""
        response = client.delete('/api/projects/nonexistent_project')
        
        # Should return 404
        assert response.status_code == 404


class TestProjectRescan:
    """Tests for POST /api/projects/<name>/rescan endpoint"""
    
    def test_rescan_existing_project(self, client, cleanup, mock_project_manager):
        """Test rescanning an existing project"""
        # Create a project first
        mock_project_manager.add_project('test_rescan_project', 'https://github.com/example/repo.git', 'main', 'python')
        
        # Rescan it
        response = client.post('/api/projects/test_rescan_project/rescan')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        assert 'rescan' in result['message'].lower()
    
    def test_rescan_nonexistent_project(self, client, mock_project_manager):
        """Test rescanning a project that doesn't exist"""
        response = client.post('/api/projects/nonexistent_project/rescan')
        
        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result


class TestProjectClear:
    """Tests for POST /api/projects/<name>/clear endpoint"""
    
    def test_clear_existing_project(self, client, cleanup, mock_project_manager):
        """Test clearing violations from a project"""
        # Create a project with violations
        mock_project_manager.add_project('test_clear_project', 'https://github.com/example/repo.git', 'main', 'python')
        project = mock_project_manager.get_project('test_clear_project')
        # Use object attributes, not dict access
        project.latest_violations = 5
        project.total_emissions = 0.0003
        
        # Clear it
        response = client.post('/api/projects/test_clear_project/clear')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ok'
        
        # Verify violations are cleared
        project = mock_project_manager.get_project('test_clear_project')
        assert project.latest_violations == 0
        assert project.total_emissions == 0.0
    
    def test_clear_nonexistent_project(self, client, mock_project_manager):
        """Test clearing a project that doesn't exist"""
        response = client.post('/api/projects/nonexistent_project/clear')
        
        assert response.status_code == 404
        result = json.loads(response.data)
        assert 'error' in result


class TestProjectEndpointIntegration:
    """Integration tests for full project lifecycle"""
    
    def test_full_project_lifecycle(self, client, cleanup, mock_project_manager):
        """Test creating, rescanning, and deleting a project"""
        # Create
        scan_data = {
            'project_name': 'test_lifecycle_project',
            'language': 'python',
            'git_url': 'https://github.com/example/repo.git'
        }

        with patch('src.ui.dashboard_app.Scanner'), \
             patch('src.ui.dashboard_app.threading.Thread'):

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
    
    def test_scan_with_special_characters_in_name(self, client, cleanup, mock_project_manager):
        """Test scan with special characters in project name"""
        data = {
            'project_name': 'test-project_v1.0',
            'language': 'python',
            'path': '/path/to/code'
        }

        with patch('src.ui.dashboard_app.Scanner'), \
             patch('src.ui.dashboard_app.threading.Thread'):
            response = client.post('/api/scan',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        assert response.status_code == 200
    
    def test_delete_with_url_encoding(self, client, cleanup, mock_project_manager):
        """Test delete with URL-encoded project name"""
        # Create project with special name
        mock_project_manager.add_project('test project with spaces', 'https://github.com/example/repo.git', 'main', 'python')
        
        # Delete with URL encoding
        response = client.delete('/api/projects/test%20project%20with%20spaces')
        
        assert response.status_code == 200
    
    def test_malformed_json_request(self, client, mock_project_manager):
        """Test API handles malformed JSON gracefully"""
        response = client.post('/api/scan',
                              data='invalid json',
                              content_type='application/json')
        
        # Should handle gracefully or return 400
        assert response.status_code in [400, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
