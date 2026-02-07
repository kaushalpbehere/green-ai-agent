"""
Tests for Project Manager module.
Verify project creation, management, and scanning operations.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.core.project_manager import Project, ProjectManager, ProjectException


class TestProject:
    """Test Project class"""
    
    def test_create_project(self):
        """Create a new project"""
        project = Project("MyApp", "https://github.com/user/myapp.git", language="python")
        assert project.name == "MyApp"
        assert project.repo_url == "https://github.com/user/myapp.git"
        assert project.language == "python"
        assert project.id is not None
        assert project.branch == "main"
        assert project.scan_count == 0
    
    def test_project_to_dict(self):
        """Convert project to dictionary"""
        project = Project("MyApp", "https://github.com/user/myapp.git", language="python")
        project.violations = [{'id': 'v1'}]
        data = project.to_dict()
        assert data['name'] == "MyApp"
        assert data['repo_url'] == "https://github.com/user/myapp.git"
        assert data['language'] == "python"
        assert 'id' in data
        assert data['violations'] == [{'id': 'v1'}]
    
    def test_project_from_dict(self):
        """Create project from dictionary"""
        data = {
            'id': 'test-123',
            'name': 'MyApp',
            'repo_url': 'https://github.com/user/myapp.git',
            'branch': 'develop',
            'language': 'python',
            'scan_count': 5,
            'latest_violations': 10,
            'total_emissions': 0.00001,
            'violations': [{'id': 'v1'}]
        }
        project = Project.from_dict(data)
        assert project.id == 'test-123'
        assert project.name == 'MyApp'
        assert project.branch == 'develop'
        assert project.scan_count == 5
        assert project.violations == [{'id': 'v1'}]
    
    def test_project_grade_no_violations(self):
        """Grade should be 'A' for no violations"""
        project = Project("App", "https://github.com/user/app.git")
        project.latest_violations = 0
        assert project.get_grade() == "A"
    
    def test_project_grade_low_violations(self):
        """Grade should be 'B' for 1-5 violations"""
        project = Project("App", "https://github.com/user/app.git")
        project.latest_violations = 3
        assert project.get_grade() == "B"
    
    def test_project_grade_medium_violations(self):
        """Grade should be 'C' for 6-10 violations"""
        project = Project("App", "https://github.com/user/app.git")
        project.latest_violations = 8
        assert project.get_grade() == "C"
    
    def test_project_grade_high_violations(self):
        """Grade should be 'D' for 11-20 violations"""
        project = Project("App", "https://github.com/user/app.git")
        project.latest_violations = 15
        assert project.get_grade() == "D"
    
    def test_project_grade_critical_violations(self):
        """Grade should be 'F' for 21+ violations"""
        project = Project("App", "https://github.com/user/app.git")
        project.latest_violations = 30
        assert project.get_grade() == "F"
    
    def test_project_update_scan_results(self):
        """Update project with scan results"""
        project = Project("App", "https://github.com/user/app.git")
        assert project.scan_count == 0
        
        # Test with int count (backward compatibility)
        project.update_scan_results(5, 0.00001)
        assert project.scan_count == 1
        assert project.latest_violations == 5
        assert project.total_emissions == 0.00001
        assert project.last_scan is not None
        
        # Test with violations list
        violations_list = [
            {'id': 'v1', 'severity': 'high'},
            {'id': 'v2', 'severity': 'medium'},
            {'id': 'v3', 'severity': 'low'}
        ]
        project.update_scan_results(violations_list, 0.00002)
        assert project.scan_count == 2
        assert project.latest_violations == 3
        assert len(project.violations) == 3
        assert project.violations[0]['id'] == 'v1'
        assert project.high_violations == 1
        assert project.medium_violations == 1
        assert project.low_violations == 1


class TestProjectManager:
    """Test ProjectManager class"""
    
    @pytest.fixture
    def manager(self, tmp_path, monkeypatch):
        """Create a ProjectManager with temporary config directory"""
        config_dir = tmp_path / ".green-ai"
        monkeypatch.setattr('src.core.project_manager.ProjectManager.CONFIG_DIR', config_dir)
        monkeypatch.setattr('src.core.project_manager.ProjectManager.REGISTRY_FILE', config_dir / "projects.json")
        monkeypatch.setattr('src.core.project_manager.ProjectManager.HISTORY_DIR', config_dir / "history")
        return ProjectManager()
    
    def test_manager_init(self, manager):
        """ProjectManager should initialize with empty projects"""
        assert len(manager.projects) == 0
        assert manager.CONFIG_DIR.exists()
    
    def test_add_project(self, manager):
        """Add project to manager"""
        project = manager.add_project("MyApp", "https://github.com/user/myapp.git", language="python")
        assert project.name == "MyApp"
        assert project.id in manager.projects
        assert len(manager.projects) == 1
    
    def test_add_duplicate_project_name(self, manager):
        """Adding duplicate project name should raise"""
        manager.add_project("MyApp", "https://github.com/user/myapp.git")
        with pytest.raises(ProjectException, match="already exists"):
            manager.add_project("MyApp", "https://github.com/user/otherapp.git")
    
    def test_get_project_by_id(self, manager):
        """Get project by ID"""
        added = manager.add_project("MyApp", "https://github.com/user/myapp.git")
        retrieved = manager.get_project(added.id)
        assert retrieved is not None
        assert retrieved.name == "MyApp"
    
    def test_get_project_by_name(self, manager):
        """Get project by name"""
        manager.add_project("MyApp", "https://github.com/user/myapp.git")
        retrieved = manager.get_project("MyApp")
        assert retrieved is not None
        assert retrieved.name == "MyApp"
    
    def test_get_nonexistent_project(self, manager):
        """Get nonexistent project should return None"""
        result = manager.get_project("nonexistent")
        assert result is None
    
    def test_list_projects_sorted_by_name(self, manager):
        """List projects sorted by name"""
        manager.add_project("Zebra", "https://github.com/user/zebra.git")
        manager.add_project("Apple", "https://github.com/user/apple.git")
        manager.add_project("Mango", "https://github.com/user/mango.git")
        
        projects = manager.list_projects(sort_by="name")
        assert [p.name for p in projects] == ["Apple", "Mango", "Zebra"]
    
    def test_list_projects_sorted_by_violations(self, manager):
        """List projects sorted by violations"""
        p1 = manager.add_project("App1", "https://github.com/user/app1.git")
        p2 = manager.add_project("App2", "https://github.com/user/app2.git")
        p3 = manager.add_project("App3", "https://github.com/user/app3.git")
        
        p1.latest_violations = 5
        p2.latest_violations = 10
        p3.latest_violations = 3
        
        projects = manager.list_projects(sort_by="violations")
        assert [p.latest_violations for p in projects] == [3, 5, 10]
    
    def test_remove_project(self, manager):
        """Remove project from manager"""
        added = manager.add_project("MyApp", "https://github.com/user/myapp.git")
        assert len(manager.projects) == 1
        
        manager.remove_project("MyApp")
        assert len(manager.projects) == 0
        assert manager.get_project("MyApp") is None
    
    def test_remove_nonexistent_project(self, manager):
        """Removing nonexistent project should raise"""
        with pytest.raises(ProjectException, match="not found"):
            manager.remove_project("nonexistent")
    
    def test_update_project_scan(self, manager):
        """Update project scan results"""
        manager.add_project("MyApp", "https://github.com/user/myapp.git")
        manager.update_project_scan("MyApp", 5, 0.00001)
        
        project = manager.get_project("MyApp")
        assert project.latest_violations == 5
        assert project.total_emissions == 0.00001
        assert project.scan_count == 1
    
    def test_update_nonexistent_project(self, manager):
        """Updating nonexistent project should raise"""
        with pytest.raises(ProjectException, match="not found"):
            manager.update_project_scan("nonexistent", 5, 0.00001)
    
    def test_get_summary_metrics_empty(self, manager):
        """Summary metrics for empty manager"""
        metrics = manager.get_summary_metrics()
        assert metrics['total_projects'] == 0
        assert metrics['total_violations'] == 0
        assert metrics['total_emissions'] == 0.0
    
    def test_get_summary_metrics_with_projects(self, manager):
        """Summary metrics with multiple projects"""
        p1 = manager.add_project("App1", "https://github.com/user/app1.git")
        p2 = manager.add_project("App2", "https://github.com/user/app2.git")
        
        p1.latest_violations = 5
        p1.total_emissions = 0.00001
        p2.latest_violations = 3
        p2.total_emissions = 0.00002
        
        metrics = manager.get_summary_metrics()
        assert metrics['total_projects'] == 2
        assert metrics['total_violations'] == 8
        assert metrics['total_emissions'] == 0.00003
        assert metrics['average_violations'] == 4.0
    
    def test_persist_and_load_projects(self, manager, tmp_path):
        """Projects should be persisted and reloaded"""
        manager.add_project("App1", "https://github.com/user/app1.git", language="python")
        manager.add_project("App2", "https://github.com/user/app2.git", language="javascript")
        
        # Create new manager instance (should reload from file)
        manager2 = ProjectManager()
        assert len(manager2.projects) == 2
        assert manager2.get_project("App1") is not None
        assert manager2.get_project("App2") is not None
    
    def test_export_projects_json(self, manager):
        """Export projects as JSON"""
        manager.add_project("App1", "https://github.com/user/app1.git")
        manager.add_project("App2", "https://github.com/user/app2.git")
        
        exported = manager.export_projects()
        data = json.loads(exported)
        
        assert data['metadata']['total_projects'] == 2
        assert len(data['projects']) == 2
        assert data['projects'][0]['name'] in ['App1', 'App2']
