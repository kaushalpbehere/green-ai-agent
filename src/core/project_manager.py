"""
Project Manager Module for Green AI Agent

Manages multiple projects, their metadata, and scan history.
Stores project registry in .green-ai/projects.json
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ProjectException(Exception):
    """Custom exception for project operations"""
    pass


class Project:
    """Represents a single project"""
    
    def __init__(
        self,
        name: str,
        repo_url: str,
        project_id: Optional[str] = None,
        branch: str = "main",
        language: Optional[str] = None,
        last_scan: Optional[str] = None,
        scan_count: int = 0,
        latest_violations: int = 0,
        total_emissions: float = 0.0,
        is_system: bool = False,
        violation_details: Optional[Dict[str, int]] = None,
        violations: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a Project.
        
        Args:
            name: Human-readable project name
            repo_url: Git repository URL (or local path)
            project_id: Unique project identifier (auto-generated if None)
            branch: Git branch (default: main)
            language: Programming language (python, javascript, etc.)
            last_scan: ISO format timestamp of last scan
            scan_count: Number of scans performed
            latest_violations: Violations count from latest scan
            total_emissions: Total CO₂ emissions in kg
            is_system: Whether this is a system project (non-deletable)
            violation_details: Dict with 'high', 'medium', 'low' counts
            violations: List of detailed violation dictionaries
        """
        self.id = project_id or str(uuid.uuid4())
        self.name = name
        self.repo_url = repo_url
        self.branch = branch or "main"
        self.language = language
        self.last_scan = last_scan
        self.scan_count = scan_count
        self.latest_violations = latest_violations
        self.total_emissions = total_emissions
        self.is_system = is_system
        self._violation_details = violation_details or {}
        self.violations = violations or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for JSON storage"""
        data = {
            "id": self.id,
            "name": self.name,
            "repo_url": self.repo_url,
            "branch": self.branch,
            "language": self.language,
            "last_scan": self.last_scan,
            "scan_count": self.scan_count,
            "latest_violations": self.latest_violations,
            "total_emissions": self.total_emissions,
            "is_system": self.is_system,
            "violations": self.violations
        }
        if self._violation_details:
            data["violation_details"] = self._violation_details
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project from dictionary"""
        return cls(
            name=data.get('name'),
            repo_url=data.get('repo_url'),
            project_id=data.get('id'),
            branch=data.get('branch', 'main'),
            language=data.get('language'),
            last_scan=data.get('last_scan'),
            scan_count=data.get('scan_count', 0),
            latest_violations=data.get('latest_violations', 0),
            total_emissions=data.get('total_emissions', 0.0),
            is_system=data.get('is_system', False),
            violation_details=data.get('violation_details'),
            violations=data.get('violations')
        )
    
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
    
    def update_scan_results(self, violations: Any, emissions: float) -> None:
        """
        Update project with new scan results.
        
        Args:
            violations: Number of violations found OR List of violation dicts
            emissions: Total emissions in kg
        """
        self.last_scan = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.scan_count += 1

        if isinstance(violations, list):
            self.violations = violations
            self.latest_violations = len(violations)

            # Update violation details
            details = {'high': 0, 'medium': 0, 'low': 0, 'critical': 0}
            for v in violations:
                severity = v.get('severity', 'low')
                if severity in details:
                    details[severity] += 1
                else:
                    details['low'] += 1
            self._violation_details = details
        else:
            self.latest_violations = violations

        self.total_emissions = round(emissions, 9)
    
    @property
    def high_violations(self) -> int:
        """
        Get count of high-severity violations.
        
        Returns:
            Count of high-severity violations
        """
        return self._violation_details.get('high', int(self.latest_violations * 0.5))
    
    @property
    def medium_violations(self) -> int:
        """
        Get count of medium-severity violations.
        
        Returns:
            Count of medium-severity violations
        """
        return self._violation_details.get('medium', int(self.latest_violations * 0.3))
    
    @property
    def low_violations(self) -> int:
        """
        Get count of low-severity violations.
        
        Returns:
            Count of low-severity violations
        """
        if 'low' in self._violation_details:
            return self._violation_details['low']
        # Approximate: remaining violations are low severity
        return self.latest_violations - self.high_violations - self.medium_violations



class ProjectManager:
    """Manage multiple projects and scan history"""
    
    CONFIG_DIR = Path.home() / ".green-ai"
    REGISTRY_FILE = CONFIG_DIR / "projects.json"
    HISTORY_DIR = CONFIG_DIR / "history"
    
    def __init__(self):
        """Initialize project manager and ensure directories exist"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Project] = {}
        self._load_projects()
    
    def _load_projects(self) -> None:
        """Load projects from registry file"""
        try:
            if self.REGISTRY_FILE.exists():
                with open(self.REGISTRY_FILE, 'r') as f:
                    data = json.load(f)
                    for project_data in data.get('projects', []):
                        project = Project.from_dict(project_data)
                        self.projects[project.id] = project
                logger.info(f"Loaded {len(self.projects)} projects from registry")
        except Exception as e:
            logger.warning(f"Error loading projects: {e}")
    
    def _save_projects(self) -> None:
        """Save projects to registry file"""
        try:
            data = {
                'projects': [p.to_dict() for p in self.projects.values()]
            }
            with open(self.REGISTRY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.projects)} projects to registry")
        except Exception as e:
            raise ProjectException(f"Error saving projects: {e}")
    
    def ensure_default_project(self) -> Project:
        """
        Ensure the default Green-AI project exists.
        If projects list is empty, auto-add Green-AI Agent as default project.
        
        Returns:
            The default Project (Green-AI Agent)
        """
        # Check if we already have the default project
        default = self.get_project("Green-AI Agent")
        if default:
            return default
        
        # If no projects exist, create the default one
        if len(self.projects) == 0:
            default = self.add_project(
                name="Green-AI Agent",
                repo_url="https://github.com/Green-AI-Agent/green-ai.git",
                branch="main",
                language="python",
                is_system=True
            )
            logger.info("Created default Green-AI Agent project")
            return default
        
        return None
    
    def add_project(
        self,
        name: str,
        repo_url: str,
        branch: str = "main",
        language: Optional[str] = None,
        is_system: bool = False
    ) -> Project:
        """
        Add a new project to the registry.
        
        Args:
            name: Project name
            repo_url: Git repository URL
            branch: Git branch (default: main)
            language: Programming language
            is_system: Whether this is a system project (non-deletable)
            
        Returns:
            Created Project object
            
        Raises:
            ProjectException: If project name already exists
        """
        # Check for duplicate names
        if any(p.name == name for p in self.projects.values()):
            raise ProjectException(f"Project '{name}' already exists")
        
        project = Project(
            name=name,
            repo_url=repo_url,
            branch=branch,
            language=language,
            is_system=is_system
        )
        self.projects[project.id] = project
        self._save_projects()
        
        logger.info(f"Added project '{name}' (ID: {project.id})" + (" [SYSTEM]" if is_system else ""))
        return project
    
    def get_project(self, project_id_or_name: str) -> Optional[Project]:
        """
        Get project by ID or name.
        
        Args:
            project_id_or_name: Project ID or name
            
        Returns:
            Project object or None if not found
        """
        # Try by ID first
        if project_id_or_name in self.projects:
            return self.projects[project_id_or_name]
        
        # Try by name
        for project in self.projects.values():
            if project.name == project_id_or_name:
                return project
        
        return None
    
    def remove_project(self, project_id_or_name: str) -> None:
        """
        Remove a project from the registry.
        
        Args:
            project_id_or_name: Project ID or name
            
        Raises:
            ProjectException: If project not found or is a system project
        """
        project = self.get_project(project_id_or_name)
        if not project:
            raise ProjectException(f"Project '{project_id_or_name}' not found")
        
        if project.is_system:
            raise ProjectException(f"Cannot delete system project '{project.name}'")
        
        del self.projects[project.id]
        self._save_projects()
        
        logger.info(f"Removed project '{project.name}'")
    
    def list_projects(self, sort_by: str = "name") -> List[Project]:
        """
        List all projects, sorted by specified field.
        
        Args:
            sort_by: Sort field (name, violations, last_scan, emissions)
            
        Returns:
            List of Project objects
        """
        projects = list(self.projects.values())
        
        sort_fields = {
            'name': lambda p: p.name.lower(),
            'violations': lambda p: p.latest_violations,
            'last_scan': lambda p: p.last_scan or "",
            'emissions': lambda p: p.total_emissions,
            'grade': lambda p: p.get_grade()
        }
        
        if sort_by in sort_fields:
            projects.sort(key=sort_fields[sort_by])
        
        return projects
    
    def update_project_scan(
        self,
        project_id_or_name: str,
        violations: Any,
        emissions: float
    ) -> None:
        """
        Update project with scan results.
        
        Args:
            project_id_or_name: Project ID or name
            violations: Number of violations OR List of violation dicts
            emissions: Total emissions in kg
            
        Raises:
            ProjectException: If project not found
        """
        project = self.get_project(project_id_or_name)
        if not project:
            raise ProjectException(f"Project '{project_id_or_name}' not found")
        
        project.update_scan_results(violations, emissions)
        self._save_projects()
        
        logger.info(
            f"Updated project '{project.name}': "
            f"{violations} violations, {emissions:.9f} kg CO₂"
        )
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Get summary metrics across all projects.
        
        Returns:
            Dict with aggregated metrics
        """
        projects = list(self.projects.values())
        
        if not projects:
            return {
                'total_projects': 0,
                'total_violations': 0,
                'total_scans': 0,
                'total_emissions': 0.0,
                'average_violations': 0,
                'average_emissions': 0.0,
                'average_grade': 'N/A'
            }
        
        total_violations = sum(p.latest_violations for p in projects)
        total_scans = sum(p.scan_count for p in projects)
        total_emissions = sum(p.total_emissions for p in projects)
        
        # Calculate average grade
        grades = [p.get_grade() for p in projects]
        grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
        avg_grade_value = sum(grade_values.get(g, 0) for g in grades) / len(grades) if grades else 3
        grade_map = {5: 'A', 4: 'B', 3: 'C', 2: 'D', 1: 'F'}
        avg_grade = grade_map.get(round(avg_grade_value), 'C')
        
        return {
            'total_projects': len(projects),
            'total_violations': total_violations,
            'total_scans': total_scans,
            'total_emissions': round(total_emissions, 9),
            'average_violations': round(total_violations / len(projects), 1) if projects else 0,
            'average_emissions': round(total_emissions / len(projects), 9) if projects else 0.0,
            'average_grade': avg_grade
        }
    
    def export_projects(self) -> str:
        """
        Export all projects as JSON string.
        
        Returns:
            JSON string representation of all projects
        """
        data = {
            'metadata': {
                'exported': datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                'total_projects': len(self.projects)
            },
            'projects': [p.to_dict() for p in self.projects.values()]
        }
        return json.dumps(data, indent=2)
