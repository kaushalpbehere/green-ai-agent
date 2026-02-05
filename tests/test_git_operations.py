"""
Tests for Git operations module.
Verify URL parsing, cloning, branch checkout, and cleanup operations.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.git_operations import GitOperations, GitException, detect_and_prepare_repository


class TestGitUrlParsing:
    """Test Git URL parsing functionality"""
    
    def test_parse_https_url_without_branch(self):
        """Parse HTTPS URL without branch specification"""
        url, branch = GitOperations.parse_git_url("https://github.com/user/repo.git")
        assert url == "https://github.com/user/repo.git"
        assert branch is None
    
    def test_parse_https_url_with_branch(self):
        """Parse HTTPS URL with @branch suffix"""
        url, branch = GitOperations.parse_git_url("https://github.com/user/repo.git@feature/optimization")
        assert url == "https://github.com/user/repo.git"
        assert branch == "feature/optimization"
    
    def test_parse_ssh_url_without_branch(self):
        """Parse SSH URL without branch specification"""
        url, branch = GitOperations.parse_git_url("git@github.com:user/repo.git")
        assert url == "git@github.com:user/repo.git"
        assert branch is None
    
    def test_parse_ssh_url_with_branch(self):
        """Parse SSH URL with @branch suffix"""
        url, branch = GitOperations.parse_git_url("git@github.com:user/repo.git@develop")
        assert url == "git@github.com:user/repo.git"
        assert branch == "develop"
    
    def test_parse_http_url(self):
        """Parse HTTP URL (less common but valid)"""
        url, branch = GitOperations.parse_git_url("http://github.com/user/repo.git")
        assert url == "http://github.com/user/repo.git"
        assert branch is None
    
    def test_parse_invalid_url_raises_exception(self):
        """Invalid URL format should raise GitException"""
        with pytest.raises(GitException):
            GitOperations.parse_git_url("invalid-url")
    
    def test_parse_empty_url_raises_exception(self):
        """Empty URL should raise GitException"""
        with pytest.raises(GitException):
            GitOperations.parse_git_url("")
    
    def test_parse_none_url_raises_exception(self):
        """None URL should raise GitException"""
        with pytest.raises(GitException):
            GitOperations.parse_git_url(None)


class TestRepoNameExtraction:
    """Test repository name extraction"""
    
    def test_extract_repo_name_from_https(self):
        """Extract repo name from HTTPS URL"""
        name = GitOperations.get_repo_name("https://github.com/user/my-repo.git")
        assert name == "my-repo"
    
    def test_extract_repo_name_from_ssh(self):
        """Extract repo name from SSH URL"""
        name = GitOperations.get_repo_name("git@github.com:user/my-repo.git")
        assert name == "my-repo"
    
    def test_extract_repo_name_with_branch(self):
        """Extract repo name from URL with branch"""
        name = GitOperations.get_repo_name("https://github.com/user/my-repo.git@feature")
        assert name == "my-repo"


class TestGitUrlDetection:
    """Test Git URL detection"""
    
    def test_is_git_url_https(self):
        """HTTPS URL should be detected as git URL"""
        assert GitOperations.is_git_url("https://github.com/user/repo.git")
    
    def test_is_git_url_ssh(self):
        """SSH URL should be detected as git URL"""
        assert GitOperations.is_git_url("git@github.com:user/repo.git")
    
    def test_is_git_url_with_branch(self):
        """URL with branch should be detected as git URL"""
        assert GitOperations.is_git_url("https://github.com/user/repo.git@main")
    
    def test_is_not_git_url_invalid(self):
        """Invalid URL should not be detected as git URL"""
        assert not GitOperations.is_git_url("invalid-url")
    
    def test_is_not_git_url_empty(self):
        """Empty string should not be detected as git URL"""
        assert not GitOperations.is_git_url("")
    
    def test_is_not_git_url_none(self):
        """None should not be detected as git URL"""
        assert not GitOperations.is_git_url(None)


class TestLocalPathDetection:
    """Test local path detection"""
    
    def test_is_local_path_existing_directory(self, tmp_path):
        """Existing directory should be detected as local path"""
        assert GitOperations.is_local_path(str(tmp_path))
    
    def test_is_not_local_path_nonexistent(self):
        """Non-existent path should not be detected as local path"""
        assert not GitOperations.is_local_path("/nonexistent/path/that/does/not/exist")
    
    def test_is_not_local_path_file(self, tmp_path):
        """File should not be detected as local path (only directories)"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert not GitOperations.is_local_path(str(test_file))
    
    def test_is_not_local_path_empty_string(self):
        """Empty string should not be detected as local path"""
        assert not GitOperations.is_local_path("")
    
    def test_is_not_local_path_none(self):
        """None should not be detected as local path"""
        assert not GitOperations.is_local_path(None)


class TestGitCloneOperation:
    """Test Git clone operations (mocked)"""
    
    @patch('subprocess.run')
    def test_clone_repository_success(self, mock_run, tmp_path):
        """Successful clone should return directory path"""
        target_dir = str(tmp_path / "repo")
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        result = GitOperations.clone_repository("https://github.com/user/repo.git", target_dir)
        
        assert result == target_dir
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_clone_repository_failure(self, mock_run):
        """Failed clone should raise GitException"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Failed to clone")
        
        with pytest.raises(GitException, match="Failed to clone repository"):
            GitOperations.clone_repository("https://github.com/user/repo.git")
    
    @patch('subprocess.run')
    def test_clone_repository_timeout(self, mock_run):
        """Timeout during clone should raise GitException"""
        mock_run.side_effect = subprocess.TimeoutExpired('git', 300)
        
        with pytest.raises(GitException, match="timed out"):
            GitOperations.clone_repository("https://github.com/user/repo.git")
    
    @patch('subprocess.run')
    def test_clone_repository_no_git_installed(self, mock_run):
        """Missing Git should raise helpful GitException"""
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(GitException, match="Git is not installed"):
            GitOperations.clone_repository("https://github.com/user/repo.git")


class TestCheckoutBranch:
    """Test branch checkout operations (mocked)"""
    
    @patch('subprocess.run')
    def test_checkout_branch_success(self, mock_run):
        """Successful checkout should not raise"""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        # Should not raise
        GitOperations.checkout_branch("/path/to/repo", "feature/new")
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_checkout_branch_failure(self, mock_run):
        """Failed checkout should raise GitException"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Branch not found")
        
        with pytest.raises(GitException, match="Failed to checkout branch"):
            GitOperations.checkout_branch("/path/to/repo", "nonexistent")
    
    def test_checkout_empty_branch_is_noop(self):
        """Checking out empty/None branch should be no-op"""
        # Should not raise
        GitOperations.checkout_branch("/path/to/repo", None)
        GitOperations.checkout_branch("/path/to/repo", "")


class TestCleanup:
    """Test repository cleanup"""
    
    def test_cleanup_nonexistent_directory(self):
        """Cleanup of nonexistent directory should not raise"""
        # Should not raise
        GitOperations.cleanup_repo("/nonexistent/path")
    
    def test_cleanup_empty_path(self):
        """Cleanup of empty path should not raise"""
        # Should not raise
        GitOperations.cleanup_repo("")
    
    def test_cleanup_none_path(self):
        """Cleanup of None should not raise"""
        # Should not raise
        GitOperations.cleanup_repo(None)
    
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    def test_cleanup_existing_directory(self, mock_rmtree, mock_exists):
        """Cleanup of existing directory should call rmtree"""
        mock_exists.return_value = True
        
        GitOperations.cleanup_repo("/path/to/repo")
        mock_rmtree.assert_called_once()


class TestDetectAndPrepare:
    """Test repository detection and preparation"""
    
    def test_detect_local_path(self, tmp_path):
        """Local directory should be detected and returned"""
        repo_dir, repo_url, branch = detect_and_prepare_repository(str(tmp_path))
        assert repo_dir == str(tmp_path)
        assert repo_url is None
        assert branch is None
    
    @patch('src.core.git_operations.GitOperations.clone_and_checkout')
    def test_detect_git_url(self, mock_clone):
        """Git URL should trigger clone_and_checkout"""
        mock_clone.return_value = ("/tmp/repo", "https://github.com/user/repo.git", "main")
        
        repo_dir, repo_url, branch = detect_and_prepare_repository("https://github.com/user/repo.git")
        
        assert repo_dir == "/tmp/repo"
        assert repo_url == "https://github.com/user/repo.git"
        assert branch == "main"
        mock_clone.assert_called_once()
    
    def test_detect_invalid_location(self):
        """Invalid location should raise GitException"""
        with pytest.raises(GitException, match="Invalid location"):
            detect_and_prepare_repository("invalid-location")


# Import subprocess at module level for timeout test
import subprocess
