"""
Unit tests for domain models (Project, Violation).
"""

import pytest
from src.core.domain import Project, Violation, ViolationSeverity

class TestDomainModels:

    def test_violation_creation(self):
        """Test creating a valid violation."""
        v = Violation(
            id="test_rule",
            line=10,
            severity=ViolationSeverity.HIGH,
            message="Test message"
        )
        assert v.severity == ViolationSeverity.HIGH
        assert v.id == "test_rule"

    def test_violation_invalid_severity(self):
        """Test normalization for invalid severity."""
        v = Violation(
            id="test_rule",
            line=10,
            severity="INVALID_SEVERITY",
            message="Test message"
        )
        assert v.severity == ViolationSeverity.INFO

    def test_project_defaults(self):
        """Test project default values."""
        from src.core.domain import ViolationDetails
        p = Project(name="Test Project", repo_url="http://example.com")
        assert p.id is not None
        assert p.branch == "main"
        assert p.violations == []
        assert isinstance(p.violation_details, ViolationDetails)
        assert p.violation_details.critical == 0
        assert p.scan_count == 0

    def test_project_get_grade(self):
        """Test grade calculation logic."""
        p = Project(name="Test", repo_url="url")

        # A
        p.latest_violations = 0
        assert p.get_grade() == "A"

        # B (1-5)
        p.latest_violations = 5
        assert p.get_grade() == "B"

        # C (6-10)
        p.latest_violations = 10
        assert p.get_grade() == "C"

        # D (11-20)
        p.latest_violations = 20
        assert p.get_grade() == "D"

        # F (>20)
        p.latest_violations = 21
        assert p.get_grade() == "F"

    def test_update_scan_results(self):
        """Test updating scan results and severity aggregation."""
        p = Project(name="Test", repo_url="url")

        violations_data = [
            {'id': 'v1', 'line': 1, 'severity': 'critical', 'message': 'm1'},
            {'id': 'v2', 'line': 2, 'severity': 'high', 'message': 'm2'},
            {'id': 'v3', 'line': 3, 'severity': 'medium', 'message': 'm3'},
            {'id': 'v4', 'line': 4, 'severity': 'minor', 'message': 'm4'},
            {'id': 'v5', 'line': 5, 'severity': 'info', 'message': 'm5'},
            {'id': 'v6', 'line': 6, 'severity': 'unknown', 'message': 'm6'}, # Should be salvaged as low or skipped
        ]

        # v6 will be skipped because severity validation fails and my code catches TypeError/ValueError
        # Wait, my code tries to salvage by setting severity to LOW.
        # Let's verify that behavior.

        p.update_scan_results(violations_data, emissions=1.23)

        # Check totals
        # v1 (critical) -> Valid
        # v2 (high) -> Valid
        # v3 (medium) -> Valid
        # v4 (minor) -> Valid
        # v5 (info) -> Valid
        # v6 (unknown) -> Valid (salvaged as LOW)

        assert len(p.violations) == 6
        assert p.latest_violations == 6
        assert p.total_emissions == 1.23

        # Check aggregation
        # High = critical + high + major (0) = 1 + 1 + 0 = 2
        assert p.high_violations == 2

        # Medium = medium (1) = 1
        assert p.medium_violations == 1

        # Low = minor + low + info = 1 + 1 (salvaged) + 1 = 3
        assert p.low_violations == 3

    def test_serialization(self):
        """Test to_dict and from_dict."""
        p = Project(name="Test", repo_url="url")
        p.language = "python"

        data = p.to_dict()
        assert data['name'] == "Test"
        assert data['language'] == "python"

        p2 = Project.from_dict(data)
        assert p2.name == p.name
        assert p2.id == p.id
