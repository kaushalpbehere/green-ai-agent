"""
Project Manager Module for Green AI Agent

Manages multiple projects, their metadata, and scan history.
Stores project registry in .green-ai/projects.json
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import logging

from src.core.domain import Project, ScanResult

logger = logging.getLogger(__name__)


class ProjectException(Exception):
    """Custom exception for project operations"""
    pass



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
            branch=branch or "main",
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
        violations: Union[ScanResult, Any],
        emissions: float = 0.0
    ) -> None:
        """
        Update project with scan results.
        
        Args:
            project_id_or_name: Project ID or name
            violations: ScanResult object, Number of violations, OR List of violation dicts
            emissions: Total emissions in kg (optional if ScanResult provided)
            
        Raises:
            ProjectException: If project not found
        """
        project = self.get_project(project_id_or_name)
        if not project:
            raise ProjectException(f"Project '{project_id_or_name}' not found")
        
        project.update_scan_results(violations, emissions)
        self._save_projects()
        
        # Determine values for logging
        count = 0
        co2 = emissions
        if isinstance(violations, ScanResult):
            count = len(violations.issues)
            co2 = violations.codebase_emissions
        elif isinstance(violations, list):
            count = len(violations)
        elif isinstance(violations, int):
            count = violations

        logger.info(
            f"Updated project '{project.name}': "
            f"{count} violations, {co2:.9f} kg CO₂"
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
