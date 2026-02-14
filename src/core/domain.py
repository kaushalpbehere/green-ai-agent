"""
Domain models for Green AI Agent.
Implements strictly typed Pydantic models for core entities.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ViolationSeverity(str, Enum):
    """Severity levels for violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MAJOR = "major"
    MEDIUM = "medium"
    MINOR = "minor"
    LOW = "low"
    INFO = "info"

class Violation(BaseModel):
    """
    Represents a single green software violation.
    """
    id: str
    line: int
    severity: ViolationSeverity
    message: str
    pattern_match: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

class ViolationDetails(BaseModel):
    """Counts of violations by severity."""
    critical: int = 0
    high: int = 0
    major: int = 0
    medium: int = 0
    minor: int = 0
    low: int = 0
    info: int = 0

    model_config = ConfigDict(extra='ignore')

class Project(BaseModel):
    """
    Represents a project being analyzed.
    Matches the schema expected by ProjectManager.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    repo_url: str
    branch: str = "main"
    language: Optional[str] = None
    last_scan: Optional[str] = None
    scan_count: int = 0
    latest_violations: int = 0
    total_emissions: float = 0.0
    is_system: bool = False
    # violation_details stores counts per severity level
    violation_details: ViolationDetails = Field(default_factory=ViolationDetails)
    violations: List[Violation] = Field(default_factory=list)

    model_config = ConfigDict(extra='ignore')

    @field_validator('violation_details', mode='before')
    @classmethod
    def set_violation_details_default(cls, v: Any) -> ViolationDetails:
        if isinstance(v, dict):
            return ViolationDetails(**v)
        return v or ViolationDetails()

    @field_validator('violations', mode='before')
    @classmethod
    def set_violations_default(cls, v: Any) -> List[Violation]:
        return v or []

    def get_grade(self) -> str:
        """
        Get project health grade (A-F) based on violations.

        Returns:
            Grade letter (A, B, C, D, F)
        """
        if self.latest_violations == 0:
            return "A"
        elif self.latest_violations <= 5:
            return "B"
        elif self.latest_violations <= 10:
            return "C"
        elif self.latest_violations <= 20:
            return "D"
        else:
            return "F"

    @property
    def high_violations(self) -> int:
        """Get count of high-severity violations (Critical + High + Major)."""
        # Aggregating critical, high, and major as 'high' impact for dashboard simplicity
        return (self.violation_details.critical +
                self.violation_details.high +
                self.violation_details.major)

    @property
    def medium_violations(self) -> int:
        """Get count of medium-severity violations."""
        return self.violation_details.medium

    @property
    def low_violations(self) -> int:
        """Get count of low-severity violations (Minor + Low + Info)."""
        # Aggregating minor, low, info as 'low' impact
        return (self.violation_details.minor +
                self.violation_details.low +
                self.violation_details.info)

    def update_scan_results(self, violations: Any, emissions: float) -> None:
        """
        Update project with new scan results.

        Args:
            violations: List of violation dicts OR integer count (for legacy/testing)
            emissions: Total emissions in kg
        """
        self.last_scan = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.scan_count += 1

        if isinstance(violations, int):
            self.latest_violations = violations
            self.violations = []
            self.violation_details = ViolationDetails()
        else:
            valid_violations = []
            details = {sev.value: 0 for sev in ViolationSeverity}

            for v_data in violations:
                try:
                    # Create Violation object (validates severity)
                    violation = Violation(**v_data)
                    valid_violations.append(violation)

                    # Update details count
                    details[violation.severity.value] += 1

                except (ValueError, TypeError):
                    # Fallback for invalid violations?
                    # For now, skip or log. We'll skip to ensure strict typing in 'violations' list.
                    # Or we could try to coerce severity to 'low'.
                    if isinstance(v_data, dict):
                         # Try to salvage with default severity
                         v_data_fixed = v_data.copy()
                         v_data_fixed['severity'] = ViolationSeverity.LOW
                         try:
                            violation = Violation(**v_data_fixed)
                            valid_violations.append(violation)
                            details[ViolationSeverity.LOW.value] += 1
                         except:
                            pass

            self.violations = valid_violations
            self.latest_violations = len(valid_violations)
            self.violation_details = ViolationDetails(**details)

        self.total_emissions = round(emissions, 9)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary."""
        return cls.model_validate(data)


class ProjectSummaryDTO(BaseModel):
    """DTO for project summary in list view."""
    id: str
    name: str
    language: Optional[str] = None
    url: str
    branch: str
    last_scan_time: Optional[str] = None
    health_grade: str
    violation_count: int
    high_violations: int
    medium_violations: int
    low_violations: int
    scanning_emissions: float
    codebase_emissions: float
    total_emissions: float
    created_date: Optional[str] = None
    created_by: str = 'system'

    model_config = ConfigDict(extra='ignore')

    @classmethod
    def from_project(cls, project: 'Project') -> 'ProjectSummaryDTO':
        return cls(
            id=project.id,
            name=project.name,
            language=project.language,
            url=project.repo_url,
            branch=project.branch,
            last_scan_time=project.last_scan,
            health_grade=project.get_grade(),
            violation_count=project.latest_violations,
            high_violations=project.high_violations,
            medium_violations=project.medium_violations,
            low_violations=project.low_violations,
            scanning_emissions=project.total_emissions, # Mapping total to scanning as per current implementation
            codebase_emissions=0,
            total_emissions=project.total_emissions,
            created_date=None,
            created_by='system'
        )

class ProjectDTO(BaseModel):
    """DTO for detailed project view."""
    id: str
    name: str
    repo_url: str
    branch: str
    language: Optional[str] = None
    last_scan: Optional[str] = None
    scan_count: int
    latest_violations: int
    total_emissions: float
    is_system: bool
    violation_details: ViolationDetails
    violations: List[Violation]
    health_grade: str

    model_config = ConfigDict(extra='ignore')

    @classmethod
    def from_project(cls, project: 'Project') -> 'ProjectDTO':
        return cls(
            id=project.id,
            name=project.name,
            repo_url=project.repo_url,
            branch=project.branch,
            language=project.language,
            last_scan=project.last_scan,
            scan_count=project.scan_count,
            latest_violations=project.latest_violations,
            total_emissions=project.total_emissions,
            is_system=project.is_system,
            violation_details=project.violation_details,
            violations=project.violations,
            health_grade=project.get_grade()
        )

class ProjectComparisonDTO(BaseModel):
    """DTO for project comparison."""
    name: str
    language: Optional[str] = None
    health_grade: str
    violation_count: int
    high_violations: int
    medium_violations: int
    low_violations: int
    scanning_emissions: float
    codebase_emissions: float
    total_emissions: float
    last_scan_time: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

    @classmethod
    def from_project(cls, project: 'Project') -> 'ProjectComparisonDTO':
        return cls(
            name=project.name,
            language=project.language,
            health_grade=project.get_grade(),
            violation_count=project.latest_violations,
            high_violations=project.high_violations,
            medium_violations=project.medium_violations,
            low_violations=project.low_violations,
            scanning_emissions=project.total_emissions,
            codebase_emissions=0,
            total_emissions=project.total_emissions,
            last_scan_time=project.last_scan
        )
