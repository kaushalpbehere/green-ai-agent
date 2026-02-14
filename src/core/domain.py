"""
Domain models for Green AI Agent.
Implements strictly typed Pydantic models for core entities.
"""

from typing import Dict, List, Optional, Any, Union
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
    Matches the schema produced by Scanner.
    """
    id: str
    file: str = "unknown"
    line: int
    severity: ViolationSeverity
    message: str
    pattern_match: Optional[str] = None
    type: str = "green_violation"
    remediation: Optional[str] = None
    ai_suggestion: Optional[str] = None
    effort: Optional[str] = "Medium"
    tags: List[str] = Field(default_factory=list)
    carbon_impact: float = 0.0
    energy_factor: Union[float, str] = 1.0  # Can be float or "100x" string in some contexts? Scanner sets it to value or default 1.
    name: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v: Any) -> ViolationSeverity:
        if isinstance(v, str):
            try:
                return ViolationSeverity(v.lower())
            except ValueError:
                return ViolationSeverity.INFO
        return v

class ScanMetadata(BaseModel):
    """Metadata about the scan."""
    total_files: int
    language: str
    path: str
    exported_at: Optional[str] = None
    project_name: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

class RuntimeMetrics(BaseModel):
    """Metrics from runtime execution (if enabled)."""
    execution_time: Optional[str] = None
    emissions: float = 0.0
    output: Optional[str] = None
    error: Optional[str] = None
    return_code: Optional[int] = None

    model_config = ConfigDict(extra='ignore')

class ScanResult(BaseModel):
    """
    Result of a codebase scan.
    Strictly typed Pydantic model replacing the legacy dictionary.
    """
    issues: List[Violation] = Field(default_factory=list)
    scanning_emissions: float = 0.0
    scanning_emissions_detailed: Dict[str, Any] = Field(default_factory=dict)
    codebase_emissions: float = 0.0
    per_file_emissions: Dict[str, float] = Field(default_factory=dict)
    runtime_metrics: Optional[RuntimeMetrics] = None
    metadata: ScanMetadata

    model_config = ConfigDict(extra='ignore')

    def get(self, key: str, default: Any = None) -> Any:
        """Helper for backward compatibility with dict-like access."""
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        return default

    def __getitem__(self, key: str) -> Any:
        """Helper for backward compatibility with dict-like access."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

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

    def update_scan_results(self, result: Union[ScanResult, Dict, int], emissions: float = 0.0) -> None:
        """
        Update project with new scan results.

        Args:
            result: ScanResult object, or legacy violations list/dict/int
            emissions: Total emissions in kg (if not provided in ScanResult)
        """
        self.last_scan = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.scan_count += 1

        valid_violations = []
        details = {sev.value: 0 for sev in ViolationSeverity}

        # Handle ScanResult object
        if isinstance(result, ScanResult):
            self.total_emissions = round(result.codebase_emissions, 9)
            valid_violations = result.issues
            for v in valid_violations:
                details[v.severity.value] += 1

        # Handle legacy int (count only)
        elif isinstance(result, int):
            self.latest_violations = result
            self.violations = []
            self.violation_details = {sev.value: 0 for sev in ViolationSeverity}
            self.total_emissions = round(emissions, 9)
            return

        # Handle legacy dict/list
        else:
            violations_data = result
            if isinstance(result, dict):
                 violations_data = result.get('issues', [])
                 self.total_emissions = result.get('codebase_emissions', emissions)
            else:
                 self.total_emissions = round(emissions, 9)

            if isinstance(violations_data, list):
                for v_data in violations_data:
                    try:
                        # Create Violation object (validates severity)
                        if isinstance(v_data, dict):
                            violation = Violation(**v_data)
                        elif isinstance(v_data, Violation):
                            violation = v_data
                        else:
                            continue

                        valid_violations.append(violation)
                        # Update details count
                        details[violation.severity.value] += 1

                    except (ValueError, TypeError):
                        if isinstance(v_data, dict):
                             # Try to salvage with default severity
                             v_data_fixed = v_data.copy()
                             if 'severity' not in v_data_fixed:
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
    violation_details: Dict[str, int]
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
