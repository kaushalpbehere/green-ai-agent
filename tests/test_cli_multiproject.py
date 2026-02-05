"""
Tests for CLI multi-project functionality
Tests the new Git URL and project management features in the CLI
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from click.testing import CliRunner
from src.cli import cli, project


class TestProjectCommands(unittest.TestCase):
    """Test project management commands"""
    
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('src.cli.ProjectManager')
    def test_project_add(self, mock_manager_class):
        """Test adding a project"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_project.return_value = None
        mock_project = Mock(id='test-id', branch='main')
        mock_manager.add_project.return_value = mock_project
        
        result = self.runner.invoke(
            project,
            ['add', 'TestProject', 'https://github.com/user/repo.git', '--language', 'python']
        )
        
        assert result.exit_code == 0
        assert 'Project added: TestProject' in result.output
        mock_manager.add_project.assert_called_once_with(
            name='TestProject',
            repo_url='https://github.com/user/repo.git',
            branch=None,
            language='python'
        )
    
    @patch('src.cli.ProjectManager')
    def test_project_add_duplicate(self, mock_manager_class):
        """Test error when adding duplicate project"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_project.return_value = Mock()  # Project exists
        
        result = self.runner.invoke(
            project,
            ['add', 'TestProject', 'https://github.com/user/repo.git']
        )
        
        assert result.exit_code == 1
        assert 'already exists' in result.output
    
    @patch('src.cli.ProjectManager')
    def test_project_list(self, mock_manager_class):
        """Test listing projects"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_project1 = Mock()
        mock_project1.name = 'Project1'
        mock_project1.language = 'python'
        mock_project1.last_scan = '2026-01-26T10:00:00Z'
        mock_project1.latest_violations = 5
        mock_project1.total_emissions = 0.001
        mock_project1.get_grade.return_value = 'B'
        
        mock_project2 = Mock()
        mock_project2.name = 'Project2'
        mock_project2.language = 'javascript'
        mock_project2.last_scan = '2026-01-26T11:00:00Z'
        mock_project2.latest_violations = 2
        mock_project2.total_emissions = 0.0005
        mock_project2.get_grade.return_value = 'A'
        
        mock_manager.list_projects.return_value = [mock_project1, mock_project2]
        mock_manager.get_summary_metrics.return_value = {
            'total_projects': 2,
            'total_violations': 7,
            'average_violations': 3.5,
            'total_scans': 2,
            'total_emissions': 0.0015,
            'average_grade': 'A'
        }
        
        result = self.runner.invoke(project, ['list'])
        
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert 'REGISTERED PROJECTS' in result.output
        assert 'Project1' in result.output
        assert 'Project2' in result.output
        assert 'Total Projects: 2' in result.output
    
    @patch('src.cli.ProjectManager')
    def test_project_list_empty(self, mock_manager_class):
        """Test listing projects when none exist"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.list_projects.return_value = []
        
        result = self.runner.invoke(project, ['list'])
        
        assert result.exit_code == 0
        assert 'No projects registered' in result.output
    
    @patch('src.cli.ProjectManager')
    def test_project_remove(self, mock_manager_class):
        """Test removing a project"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.remove_project.return_value = True
        
        result = self.runner.invoke(
            project,
            ['remove', 'TestProject', '--yes']
        )
        
        assert result.exit_code == 0
        assert 'Project removed: TestProject' in result.output
    
    @patch('src.cli.ProjectManager')
    def test_project_remove_not_found(self, mock_manager_class):
        """Test error when removing non-existent project"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.remove_project.return_value = False
        
        result = self.runner.invoke(
            project,
            ['remove', 'NonExistent', '--yes']
        )
        
        assert result.exit_code == 1
        assert 'not found' in result.output
    
    @patch('src.cli.ProjectManager')
    def test_project_export(self, mock_manager_class):
        """Test exporting projects as JSON"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.export_projects.return_value = '{"projects": []}'
        
        result = self.runner.invoke(project, ['export'])
        
        assert result.exit_code == 0
        assert '{"projects": []}' in result.output


class TestScanCommandValidation(unittest.TestCase):
    """Test scan command validation logic"""
    
    def setUp(self):
        self.runner = CliRunner()
    
    def test_scan_missing_path_and_git_url(self):
        """Test error when neither PATH nor --git-url provided"""
        result = self.runner.invoke(cli, ['scan'])
        
        assert result.exit_code == 1
        assert 'Either PATH or --git-url must be provided' in result.output


if __name__ == '__main__':
    unittest.main()
