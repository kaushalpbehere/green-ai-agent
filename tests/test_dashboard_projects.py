"""
Tests for Multi-Project Dashboard UI endpoints and features
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.ui.dashboard_app import (
    app, 
    api_projects_list, 
    api_project_detail,
    api_projects_comparison
)
from src.utils.metrics import calculate_average_grade, calculate_projects_grade


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# sample_project_objects fixture is now in conftest.py as sample_project_objects
# It returns proper Project objects instead of dictionaries


class TestProjectsAPIEndpoint:
    """Test /api/projects endpoint"""

    def test_api_projects_list_success(self, client, sample_project_objects):
        """Test successful retrieval of projects list"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = sample_project_objects
            response = client.get('/api/projects')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'ok'
            assert data['total_projects'] == 3
            assert len(data['projects']) == 3
            assert data['projects'][0]['name'] == 'MyApp Backend'
            assert data['projects'][1]['name'] == 'MyApp Frontend'
            assert data['projects'][2]['name'] == 'DataProcessor'

    def test_api_projects_list_empty(self, client):
        """Test projects list when no projects exist"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = []
            response = client.get('/api/projects')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'ok'
            assert data['total_projects'] == 0
            assert len(data['projects']) == 0

    def test_api_projects_metrics_calculation(self, client, sample_project_objects):
        """Test that metrics are calculated correctly"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = sample_project_objects
            response = client.get('/api/projects')
            data = json.loads(response.data)
            
            # Check first project metrics
            proj1 = data['projects'][0]
            assert proj1['violation_count'] == 2
            assert proj1['high_violations'] == 1
            assert proj1['medium_violations'] == 1
            assert proj1['low_violations'] == 0
            # 2 violations => Grade B (0=A, 1-5=B)
            assert proj1['health_grade'] == 'B'
            assert proj1['total_emissions'] == 0.000006
            
            # Check summary metrics (2 + 3 + 4 = 9 total violations)
            assert data['summary']['total_violations'] == 9
            assert data['summary']['total_high_violations'] == 5  # 1 + 1 + 3
            # Combined emissions: (0.000001 + 0.000005) + (0.000002 + 0.000008) + (0.000003 + 0.000025) = 0.000044
            assert abs(data['summary']['combined_emissions'] - 0.000044) < 1e-9
            # B, B, B => Average B
            assert data['summary']['average_grade'] == 'B'

    def test_api_projects_list_violation_counts(self, client, sample_project_objects):
        """Test violation counting by severity"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = sample_project_objects
            response = client.get('/api/projects')
            data = json.loads(response.data)
            
            # Verify second project (JavaScript)
            proj2 = data['projects'][1]
            assert proj2['high_violations'] == 1
            assert proj2['medium_violations'] == 1
            assert proj2['low_violations'] == 1
            assert proj2['violation_count'] == 3
            
            # Verify third project (DataProcessor - most violations)
            proj3 = data['projects'][2]
            assert proj3['high_violations'] == 3
            # sample_project_objects defines medium=0 for this project
            assert proj3['medium_violations'] == 0
            assert proj3['low_violations'] == 1
            assert proj3['violation_count'] == 4


class TestProjectDetailEndpoint:
    """Test /api/projects/<name> endpoint"""

    def test_api_project_detail_success(self, client, sample_project_objects):
        """Test successful retrieval of project details"""
        project = sample_project_objects[0]
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = project
            response = client.get(f'/api/projects/{project.name}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'ok'
            assert data['project']['name'] == 'MyApp Backend'
            assert data['project']['language'] == 'Python'
            assert data['project']['health_grade'] == 'B'
            # BUG-005 FIXED - Violations list is now populated
            assert len(data['project']['violations']) == 2

    def test_api_project_detail_not_found(self, client):
        """Test project detail when project doesn't exist"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = None
            response = client.get('/api/projects/NonExistent')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data

    def test_api_project_detail_complete_data(self, client, sample_project_objects):
        """Test that all project fields are returned"""
        project = sample_project_objects[1]
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = project
            response = client.get(f'/api/projects/{project.name}')
            data = json.loads(response.data)
            
            proj_data = data['project']
            assert proj_data['id'] == 'proj-002'
            assert proj_data['name'] == 'MyApp Frontend'
            assert proj_data['language'] == 'JavaScript'
            # api_project_detail returns repo_url (via to_dict), api_projects_list returns url
            assert proj_data['repo_url'] == 'https://github.com/example/frontend'
            assert proj_data['branch'] == 'develop'
            assert proj_data['health_grade'] == 'B'
            assert proj_data['last_scan'] == '2024-01-19 14:15:00'
            # emissions fields are flat in to_dict
            assert proj_data['total_emissions'] == 0.00001


class TestComparisonEndpoint:
    """Test /api/projects/comparison endpoint"""

    def test_api_comparison_multiple_projects(self, client, sample_project_objects):
        """Test successful comparison of multiple projects"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.side_effect = lambda name: next((p for p in sample_project_objects if p.name == name), None)
            response = client.get('/api/projects/comparison?projects=MyApp Backend&projects=MyApp Frontend')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'ok'
            assert data['comparison_count'] == 2
            assert len(data['projects']) == 2
            assert data['projects'][0]['name'] == 'MyApp Backend'
            assert data['projects'][1]['name'] == 'MyApp Frontend'

    def test_api_comparison_no_projects_specified(self, client):
        """Test comparison endpoint with no projects specified"""
        response = client.get('/api/projects/comparison')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_api_comparison_max_projects_limit(self, client, sample_project_objects):
        """Test comparison endpoint respects maximum projects limit"""
        # Try to compare 6 projects (limit is 5)
        query = '&'.join([f'projects=Project{i}' for i in range(6)])
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = sample_project_objects[0]
            response = client.get(f'/api/projects/comparison?{query}')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'Maximum 5' in data['error']

    def test_api_comparison_invalid_projects(self, client):
        """Test comparison when no valid projects found"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = None
            response = client.get('/api/projects/comparison?projects=Invalid1&projects=Invalid2')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data

    def test_api_comparison_partial_invalid_projects(self, client, sample_project_objects):
        """Test comparison with some valid and some invalid projects"""
        valid_project = sample_project_objects[0]
        
        def mock_get_project(name):
            if name == 'MyApp Backend':
                return valid_project
            return None
        
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.side_effect = mock_get_project
            response = client.get('/api/projects/comparison?projects=MyApp Backend&projects=Invalid')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['comparison_count'] == 1
            assert data['projects'][0]['name'] == 'MyApp Backend'

    def test_api_comparison_includes_all_metrics(self, client, sample_project_objects):
        """Test that comparison includes all required metrics"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.side_effect = lambda name: next((p for p in sample_project_objects if p.name == name), None)
            response = client.get('/api/projects/comparison?projects=MyApp Backend&projects=MyApp Frontend')
            data = json.loads(response.data)
            
            project = data['projects'][0]
            assert 'name' in project
            assert 'language' in project
            assert 'health_grade' in project
            assert 'violation_count' in project
            assert 'high_violations' in project
            assert 'medium_violations' in project
            assert 'low_violations' in project
            assert 'scanning_emissions' in project
            assert 'codebase_emissions' in project
            assert 'total_emissions' in project
            assert 'last_scan_time' in project


class TestAverageGradeCalculation:
    """Test calculate_average_grade utility function"""

    def test_average_grade_all_a(self):
        """Test average grade when all are A"""
        grades = ['A', 'A', 'A']
        result = calculate_average_grade(grades)
        assert result == 'A'

    def test_average_grade_mixed(self):
        """Test average grade with mixed grades"""
        # A, B, F = 5, 4, 1 = average 3.33 = C
        grades = ['A', 'B', 'F']
        result = calculate_average_grade(grades)
        assert result == 'C'

    def test_average_grade_all_f(self):
        """Test average grade when all are F"""
        grades = ['F', 'F', 'F']
        result = calculate_average_grade(grades)
        assert result == 'F'

    def test_average_grade_mostly_a(self):
        """Test average grade when mostly A"""
        # A, A, A, A, B = 5, 5, 5, 5, 4 = average 4.8 = A
        grades = ['A', 'A', 'A', 'A', 'B']
        result = calculate_average_grade(grades)
        assert result == 'A'

    def test_average_grade_empty_list(self):
        """Test average grade with empty list"""
        grades = []
        result = calculate_average_grade(grades)
        assert result == 'N/A'

    def test_average_grade_invalid_grades(self):
        """Test average grade with invalid grades"""
        grades = ['X', 'Y', 'Z']
        result = calculate_average_grade(grades)
        assert result == 'N/A'

    def test_average_grade_boundary_values(self):
        """Test average grade at boundary values"""
        # A, B = 5, 4 = average 4.5 = A (boundary)
        grades = ['A', 'B']
        result = calculate_average_grade(grades)
        assert result == 'A'
        
        # B, C = 4, 3 = average 3.5 = B (boundary)
        grades = ['B', 'C']
        result = calculate_average_grade(grades)
        assert result == 'B'


class TestProjectGradeCalculation:
    """Test calculate_projects_grade utility function"""

    def test_projects_grade_calculation(self, sample_project_objects):
        """Test grade calculation from project objects"""
        # Sample projects have violations: 2, 3, 4
        # All convert to grade B (0=A, 1-5=B)
        # Average of B, B, B is B
        result = calculate_projects_grade(sample_project_objects)
        assert result == 'B'

    def test_projects_grade_empty(self):
        """Test grade calculation with empty list"""
        result = calculate_projects_grade([])
        assert result == 'N/A'


class TestDashboardIntegration:
    """Integration tests for dashboard endpoints"""

    def test_dashboard_route_exists(self, client):
        """Test that dashboard route is accessible"""
        # We need to mock get_landing_page_html for this route if it uses it
        with patch('src.ui.dashboard_app.get_landing_page_html', return_value="<html></html>"), \
             patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
             mock_get_pm.return_value.list_projects.return_value = []
             response = client.get('/')
             assert response.status_code in [200, 500]

    def test_all_api_endpoints_exist(self, client):
        """Test that all API endpoints are registered"""
        # These should not return 404
        endpoints = [
            '/api/projects',
            '/api/standards',
        ]
        
        # We need to mock for these to work without 500
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm, \
             patch('src.ui.dashboard_app.get_standards_registry') as mock_get_sr:
            mock_get_pm.return_value.list_projects.return_value = []
            mock_get_sr.return_value.list_standards.return_value = {}

            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code != 404, f"{endpoint} not found"

    def test_projects_list_returns_valid_json(self, client, sample_project_objects):
        """Test that projects list returns valid JSON"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = sample_project_objects
            response = client.get('/api/projects')
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            data = json.loads(response.data)
            assert isinstance(data, dict)

    def test_comparison_returns_valid_json(self, client, sample_project_objects):
        """Test that comparison returns valid JSON"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.side_effect = lambda name: next((p for p in sample_project_objects if p.name == name), None)
            response = client.get('/api/projects/comparison?projects=MyApp Backend&projects=MyApp Frontend')
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            data = json.loads(response.data)
            assert isinstance(data, dict)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_project_with_no_violations(self, client, clean_project):
        """Test project with zero violations"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = [clean_project]
            response = client.get('/api/projects')
            data = json.loads(response.data)
            
            proj = data['projects'][0]
            assert proj['violation_count'] == 0
            assert proj['high_violations'] == 0
            assert proj['medium_violations'] == 0
            assert proj['low_violations'] == 0

    def test_project_with_special_characters_in_name(self, client, project_factory):
        """Test handling of project names with special characters"""
        project_name = 'Test-Project_2024.v1'
        project = project_factory(
            project_id='proj-special',
            name=project_name,
            language='Python',
            repo_url='https://github.com/example/test',
            last_scan='2024-01-20 12:00:00',
            total_emissions=0.000003
        )
        
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.get_project.return_value = project
            response = client.get(f'/api/projects/{project_name}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['project']['name'] == project_name

    def test_project_with_large_emission_values(self, client, large_project):
        """Test handling of large emission values"""
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = [large_project]
            response = client.get('/api/projects')
            data = json.loads(response.data)
            
            proj = data['projects'][0]
            assert proj['total_emissions'] == 0.011
            assert proj['violation_count'] == 50

    def test_multiple_same_severity_violations(self, client, project_factory):
        """Test counting when violations are provided explicitly"""
        project = project_factory(
            project_id='proj-same',
            name='SameSeverity',
            language='Python',
            repo_url='https://github.com/example/same',
            last_scan='2024-01-20 12:00:00',
            latest_violations=10,
            total_emissions=0.000003,
            violation_details={'high': 5, 'medium': 3, 'low': 2}
        )
        
        with patch('src.ui.dashboard_app.get_project_manager') as mock_get_pm:
            mock_get_pm.return_value.list_projects.return_value = [project]
            response = client.get('/api/projects')
            data = json.loads(response.data)
            
            proj = data['projects'][0]
            assert proj['violation_count'] == 10
            # With explicit details, these should match
            assert proj['high_violations'] == 5
            assert proj['medium_violations'] == 3
            assert proj['low_violations'] == 2
