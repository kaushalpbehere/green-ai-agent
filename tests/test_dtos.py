import pytest
from src.core.domain import Project, ProjectSummaryDTO, ProjectDTO, ProjectComparisonDTO, ViolationSeverity, Violation

def test_project_summary_dto():
    project = Project(name="Test Project", repo_url="http://example.com")
    project.latest_violations = 5
    project.total_emissions = 1.23

    dto = ProjectSummaryDTO.from_project(project)

    assert dto.name == "Test Project"
    assert dto.url == "http://example.com"
    assert dto.violation_count == 5
    assert dto.total_emissions == 1.23
    assert dto.health_grade == "B" # 5 violations = B

def test_project_dto():
    from src.core.domain import ViolationDetails
    project = Project(name="Test Project", repo_url="http://example.com")
    project.latest_violations = 15
    project.violation_details = ViolationDetails(medium=15)

    dto = ProjectDTO.from_project(project)

    assert dto.name == "Test Project"
    assert dto.latest_violations == 15
    assert dto.health_grade == "D" # 15 violations = D
    assert dto.violation_details.medium == 15

def test_project_comparison_dto():
    from src.core.domain import ViolationDetails
    project = Project(name="Test Project", repo_url="http://example.com")
    project.latest_violations = 2
    project.violation_details = ViolationDetails(low=2)
    project.total_emissions = 0.5

    dto = ProjectComparisonDTO.from_project(project)

    assert dto.name == "Test Project"
    assert dto.violation_count == 2
    assert dto.low_violations == 2
    assert dto.total_emissions == 0.5
    assert dto.health_grade == "B" # 2 violations = B
