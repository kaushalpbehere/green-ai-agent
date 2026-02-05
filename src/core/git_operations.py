"""
Git Operations Module for Green AI Agent

Handles cloning repositories, branch management, and cleanup.
Supports multiple git URL formats and SSH/HTTPS protocols.
"""

import subprocess
import shutil
import os
from pathlib import Path
from typing import Tuple, Optional
import tempfile
import logging

logger = logging.getLogger(__name__)


class GitException(Exception):
    """Custom exception for Git operations"""
    pass


class GitOperations:
    """Handle Git repository operations"""
    
    TEMP_BASE_DIR = Path(tempfile.gettempdir()) / "green-ai-repos"
    
    @classmethod
    def parse_git_url(cls, url: str) -> Tuple[str, Optional[str]]:
        """
        Parse git URL and extract repository URL and branch (if specified).
        
        Supported formats:
        - https://github.com/user/repo.git
        - https://github.com/user/repo.git@branch-name
        - git@github.com:user/repo.git
        - git@github.com:user/repo.git@develop
        
        Args:
            url: Git URL with optional @branch suffix
            
        Returns:
            Tuple of (repo_url, branch_name) where branch_name is None for main/master
            
        Raises:
            GitException: If URL format is invalid
        """
        if not url or not isinstance(url, str):
            raise GitException(f"Invalid git URL: {url}")
        
        # Check for branch specification (suffix with @)
        branch = None
        if '@' in url and not url.startswith('git@'):
            # HTTPS URL with branch: https://github.com/user/repo.git@branch
            parts = url.rsplit('@', 1)
            url = parts[0]
            branch = parts[1]
        elif url.startswith('git@') and url.count('@') > 1:
            # SSH URL with branch: git@github.com:user/repo.git@branch
            parts = url.rsplit('@', 1)
            url = parts[0]
            branch = parts[1]
        
        # Validate URL format
        if not (url.startswith('https://') or url.startswith('git@') or url.startswith('http://')):
            raise GitException(
                f"Invalid git URL format: {url}. "
                "Expected https://, git@, or http://"
            )
        
        return url, branch
    
    @classmethod
    def clone_repository(cls, repo_url: str, target_dir: Optional[str] = None) -> str:
        """
        Clone a Git repository to a temporary directory.
        
        Args:
            repo_url: URL of the repository to clone
            target_dir: Optional specific directory (if None, uses temp directory)
            
        Returns:
            Path to the cloned repository
            
        Raises:
            GitException: If clone fails
        """
        if target_dir is None:
            # Create temp directory if needed
            cls.TEMP_BASE_DIR.mkdir(parents=True, exist_ok=True)
            # Generate unique directory name from repo URL
            repo_name = repo_url.split('/')[-1].replace('.git', '').replace('@', '_')
            import uuid
            target_dir = str(cls.TEMP_BASE_DIR / f"{repo_name}_{uuid.uuid4().hex[:8]}")
        
        try:
            logger.info(f"Cloning repository: {repo_url} to {target_dir}")
            result = subprocess.run(
                ['git', 'clone', repo_url, target_dir],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise GitException(f"Failed to clone repository: {result.stderr}")
            
            logger.info(f"Successfully cloned repository to {target_dir}")
            return target_dir
            
        except subprocess.TimeoutExpired:
            raise GitException("Git clone operation timed out (5 minutes)")
        except FileNotFoundError:
            raise GitException(
                "Git is not installed or not in PATH. "
                "Please install Git: https://git-scm.com/downloads"
            )
        except Exception as e:
            raise GitException(f"Unexpected error during clone: {str(e)}")
    
    @classmethod
    def get_default_branch(cls, repo_dir: str) -> str:
        """
        Get the default branch of a repository (main or master).
        
        Args:
            repo_dir: Path to the cloned repository
            
        Returns:
            Name of the default branch (usually 'main' or 'master')
            
        Raises:
            GitException: If operation fails
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                return current_branch
            
            # Fallback: check for main or master
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            branches = result.stdout.strip().split('\n')
            for branch in ['main', 'master']:
                if any(branch in b for b in branches):
                    return branch
            
            # Default to first branch
            if branches:
                first_branch = branches[0].strip().replace('*', '').strip()
                return first_branch
            
            return 'main'
            
        except Exception as e:
            logger.warning(f"Could not determine default branch: {e}")
            return 'main'
    
    @classmethod
    def checkout_branch(cls, repo_dir: str, branch: str) -> None:
        """
        Checkout a specific branch in the repository.
        
        Args:
            repo_dir: Path to the repository
            branch: Branch name to checkout
            
        Raises:
            GitException: If checkout fails
        """
        if not branch:
            return
        
        try:
            logger.info(f"Checking out branch '{branch}' in {repo_dir}")
            result = subprocess.run(
                ['git', 'checkout', branch],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise GitException(
                    f"Failed to checkout branch '{branch}': {result.stderr}"
                )
            
            logger.info(f"Successfully checked out branch '{branch}'")
            
        except subprocess.TimeoutExpired:
            raise GitException(f"Checkout operation for branch '{branch}' timed out")
        except Exception as e:
            raise GitException(f"Error checking out branch '{branch}': {str(e)}")
    
    @classmethod
    def cleanup_repo(cls, repo_dir: str) -> None:
        """
        Remove a cloned repository directory.
        
        Args:
            repo_dir: Path to the repository to remove
        """
        if not repo_dir or not os.path.exists(repo_dir):
            return
        
        try:
            logger.info(f"Cleaning up repository at {repo_dir}")
            shutil.rmtree(repo_dir, ignore_errors=True)
            logger.info(f"Successfully removed repository directory")
        except Exception as e:
            logger.warning(f"Error cleaning up repository: {e}")
    
    @classmethod
    def clone_and_checkout(cls, git_url: str, target_dir: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
        """
        Clone a repository and checkout the specified branch (or default).
        
        Args:
            git_url: Git URL (with optional @branch suffix)
            target_dir: Optional target directory
            
        Returns:
            Tuple of (repo_dir, repo_url, branch_name)
            
        Raises:
            GitException: If any operation fails
        """
        # Parse URL and branch
        repo_url, branch = cls.parse_git_url(git_url)
        
        # Clone repository
        repo_dir = cls.clone_repository(repo_url, target_dir)
        
        # If branch not specified, use default
        if not branch:
            branch = cls.get_default_branch(repo_dir)
        
        # Checkout branch
        cls.checkout_branch(repo_dir, branch)
        
        return repo_dir, repo_url, branch
    
    @classmethod
    def get_repo_name(cls, git_url: str) -> str:
        """
        Extract repository name from git URL.
        
        Args:
            git_url: Git URL
            
        Returns:
            Repository name (without .git suffix)
        """
        url, _ = cls.parse_git_url(git_url)
        repo_name = url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        return repo_name
    
    @classmethod
    def is_git_url(cls, url: str) -> bool:
        """
        Check if a string is a git URL.
        
        Args:
            url: String to check
            
        Returns:
            True if it's a valid git URL, False otherwise
        """
        try:
            if not url or not isinstance(url, str):
                return False
            cls.parse_git_url(url)
            return True
        except GitException:
            return False
    
    @classmethod
    def is_local_path(cls, path: str) -> bool:
        """
        Check if a path is a local directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists and is a directory, False otherwise
        """
        if not path or not isinstance(path, str):
            return False
        return os.path.isdir(path)


def detect_and_prepare_repository(location: str) -> Tuple[str, Optional[str], str]:
    """
    Detect if location is a git URL or local path and prepare it.
    
    Args:
        location: Git URL, git URL with branch (@branch), or local path
        
    Returns:
        Tuple of (repo_dir, repo_url, branch_name)
        - repo_dir: Path to repository (local or cloned)
        - repo_url: The repository URL (None for local paths)
        - branch_name: The branch name (None for local paths)
        
    Raises:
        GitException: If neither valid git URL nor local path
    """
    # Check if it's a git URL
    if GitOperations.is_git_url(location):
        repo_dir, repo_url, branch = GitOperations.clone_and_checkout(location)
        return repo_dir, repo_url, branch
    
    # Check if it's a local path
    if GitOperations.is_local_path(location):
        return location, None, None
    
    raise GitException(
        f"Invalid location: '{location}'. "
        "Expected either a git URL (https://..., git@...) or a local directory path."
    )
