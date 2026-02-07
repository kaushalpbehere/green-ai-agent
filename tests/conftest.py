"""
Test fixtures and factories for Green AI Agent tests.

Provides reusable test data and factory functions for creating
Project objects and other test entities.
"""

import pytest
from src.core.project_manager import Project


@pytest.fixture
def project_factory():
    """
    Factory fixture for creating Project objects with test data.
    
    Returns a function that creates Project instances with customizable attributes.
    This ensures tests use actual Project objects instead of dictionaries.
    """
    def _create_project(
        name="TestProject",
        repo_url="https://github.com/test/repo",
        project_id=None,
        branch="main",
        language="Python",
        last_scan=None,
        scan_count=0,
        latest_violations=0,
        total_emissions=0.0,
        is_system=False,
        violation_details=None,
        violations=None
    ):
        """Create a Project object with specified or default values."""
        return Project(
            name=name,
            repo_url=repo_url,
            project_id=project_id,
            branch=branch,
            language=language,
            last_scan=last_scan,
            scan_count=scan_count,
            latest_violations=latest_violations,
            total_emissions=total_emissions,
            is_system=is_system,
            violation_details=violation_details,
            violations=violations
        )
    
    return _create_project


@pytest.fixture
def sample_project_objects(project_factory):
    """
    Fixture providing a list of realistic Project objects for testing.
    
    Replaces the old dictionary-based sample_projects fixture.
    Returns Project objects that match the expected API structure.
    """
    return [
        project_factory(
            project_id='proj-001',
            name='MyApp Backend',
            language='Python',
            repo_url='https://github.com/example/backend',
            branch='main',
            last_scan='2024-01-20 10:30:00',
            latest_violations=2,
            total_emissions=0.000006,
            scan_count=5,
            violation_details={'high': 1, 'medium': 1, 'low': 0},
            violations=[
                {'id': 'vio1', 'severity': 'high', 'message': 'High violation'},
                {'id': 'vio2', 'severity': 'medium', 'message': 'Medium violation'}
            ]
        ),
        project_factory(
            project_id='proj-002',
            name='MyApp Frontend',
            language='JavaScript',
            repo_url='https://github.com/example/frontend',
            branch='develop',
            last_scan='2024-01-19 14:15:00',
            latest_violations=3,
            total_emissions=0.00001,
            scan_count=3,
            violation_details={'high': 1, 'medium': 1, 'low': 1}
        ),
        project_factory(
            project_id='proj-003',
            name='DataProcessor',
            language='Python',
            repo_url='https://github.com/example/processor',
            branch='main',
            last_scan='2024-01-18 08:00:00',
            latest_violations=4,
            total_emissions=0.000028,
            scan_count=10,
            violation_details={'high': 3, 'medium': 0, 'low': 1}
        ),
    ]


@pytest.fixture
def clean_project(project_factory):
    """Project with zero violations for edge case testing."""
    return project_factory(
        project_id='proj-clean',
        name='CleanProject',
        language='Python',
        repo_url='https://github.com/example/clean',
        last_scan='2024-01-20 12:00:00',
        latest_violations=0,
        total_emissions=0.000002
    )


@pytest.fixture
def large_project(project_factory):
    """Project with many violations for stress testing."""
    return project_factory(
        project_id='proj-large',
        name='LargeProject',
        language='Java',
        repo_url='https://github.com/example/large',
        last_scan='2024-01-20 12:00:00',
        latest_violations=50,
        total_emissions=0.011
    )
