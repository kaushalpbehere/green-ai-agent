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
    violation_details: Dict[str, int] = Field(default_factory=dict)
    violations: List[Violation] = Field(default_factory=list)

    model_config = ConfigDict(extra='ignore')

    @field_validator('violation_details', mode='before')
    @classmethod
    def set_violation_details_default(cls, v: Any) -> Dict[str, int]:
        return v or {}

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
        return (self.violation_details.get('critical', 0) +
                self.violation_details.get('high', 0) +
                self.violation_details.get('major', 0))

    @property
    def medium_violations(self) -> int:
        """Get count of medium-severity violations."""
        return self.violation_details.get('medium', 0)

    @property
    def low_violations(self) -> int:
        """Get count of low-severity violations (Minor + Low + Info)."""
        # Aggregating minor, low, info as 'low' impact
        return (self.violation_details.get('minor', 0) +
                self.violation_details.get('low', 0) +
                self.violation_details.get('info', 0))

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
            self.violation_details = {sev.value: 0 for sev in ViolationSeverity}
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
            self.violation_details = details

        self.total_emissions = round(emissions, 9)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary."""
        return cls.model_validate(data)
