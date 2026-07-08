import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.cli.commands.ci import ci

@pytest.fixture
def runner():
    return CliRunner()

def test_comment_no_args(runner):
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1'])
    assert result.exit_code == 1
    assert "Either --body or --file must be provided" in result.output

def test_comment_both_args(runner, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("test")
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--body', 'b', '--file', str(f)])
    assert result.exit_code == 1
    assert "Cannot provide both --body and --file" in result.output

def test_comment_bad_file(runner):
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--file', 'nonexistent.txt'])
    assert result.exit_code == 2

@patch('src.cli.commands.ci.GitHubClient')
def test_comment_success_body(mock_client_class, runner):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--body', 'test comment'])
    assert result.exit_code == 0
    assert "Successfully posted comment" in result.output
    mock_client.post_comment.assert_called_once_with('owner', 'repo', 1, 'test comment')

@patch('src.cli.commands.ci.GitHubClient')
def test_comment_success_file(mock_client_class, runner, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    f = tmp_path / "test.txt"
    f.write_text("file comment")
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--file', str(f)])
    assert result.exit_code == 0
    assert "Successfully posted comment" in result.output
    mock_client.post_comment.assert_called_once_with('owner', 'repo', 1, 'file comment')

def test_comment_bad_repo(runner):
    result = runner.invoke(ci, ['comment', '--repo', 'badrepo', '--pr', '1', '--body', 'b'])
    assert result.exit_code == 1
    assert "Repo must be in format owner/repo" in result.output

@patch('src.cli.commands.ci.GitHubClient')
def test_comment_value_error(mock_client_class, runner):
    mock_client_class.side_effect = ValueError("No token")
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--body', 'b'])
    assert result.exit_code == 1
    assert "No token" in result.output

@patch('src.cli.commands.ci.GitHubClient')
def test_comment_general_error(mock_client_class, runner):
    mock_client = MagicMock()
    mock_client.post_comment.side_effect = Exception("API error")
    mock_client_class.return_value = mock_client
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--body', 'b'])
    assert result.exit_code == 1
    assert "Failed to post comment" in result.output

@patch('src.cli.commands.ci.GitHubClient')
@patch('src.cli.commands.ci.CIReporter')
def test_report_success(mock_reporter_class, mock_client_class, runner, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_reporter = MagicMock()
    mock_reporter.generate_report.return_value = "markdown"
    mock_reporter_class.return_value = mock_reporter

    f = tmp_path / "results.json"
    f.write_text("{}")

    result = runner.invoke(ci, ['report', '--scan-results', str(f), '--repo', 'owner/repo', '--pr', '1'])
    assert result.exit_code == 0
    assert "Successfully posted report" in result.output
    mock_client.post_comment.assert_called_once_with('owner', 'repo', 1, 'markdown')

@patch('src.cli.commands.ci.GitHubClient')
@patch('src.cli.commands.ci.CIReporter')
def test_report_with_diff(mock_reporter_class, mock_client_class, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.get_pr_diff.return_value = "diff text"
    mock_client.parse_diff.return_value = {"file.py": {1}}
    mock_client_class.return_value = mock_client

    mock_reporter = MagicMock()
    mock_reporter.generate_report.return_value = "markdown"
    mock_reporter_class.return_value = mock_reporter

    f = tmp_path / "results.json"
    f.write_text("{}")

    result = runner.invoke(ci, ['report', '--scan-results', str(f), '--repo', 'owner/repo', '--pr', '1', '--filter-diff'])
    assert result.exit_code == 0
    mock_client.get_pr_diff.assert_called_once_with('owner', 'repo', 1)
    mock_client.parse_diff.assert_called_once_with("diff text")
    mock_reporter.generate_report.assert_called_once_with({}, {"file.py": {1}})

def test_report_bad_repo(runner, tmp_path):
    f = tmp_path / "results.json"
    f.write_text("{}")
    result = runner.invoke(ci, ['report', '--scan-results', str(f), '--repo', 'badrepo', '--pr', '1'])
    assert result.exit_code == 1
    assert "Repo must be in format owner/repo" in result.output

@patch('src.cli.commands.ci.GitHubClient')
def test_report_error(mock_client_class, runner, tmp_path):
    mock_client_class.side_effect = Exception("error")
    f = tmp_path / "results.json"
    f.write_text("{}")
    result = runner.invoke(ci, ['report', '--scan-results', str(f), '--repo', 'owner/repo', '--pr', '1'])
    assert result.exit_code == 1
    assert "Failed to post report" in result.output

@patch('src.cli.commands.ci.StandardsSyncEngine')
def test_check_standards_ok(mock_engine_class, runner):
    mock_engine = MagicMock()
    mock_engine.check_stale.return_value = {"src1": False}
    mock_entry = MagicMock()
    mock_entry.last_sync = "2023-01-01"
    mock_engine.manifest.entries = {"src1": mock_entry}
    mock_engine_class.return_value = mock_engine

    result = runner.invoke(ci, ['check-standards'])
    assert result.exit_code == 0
    assert "All standards are within the freshness threshold" in result.output

@patch('src.cli.commands.ci.StandardsSyncEngine')
def test_check_standards_stale_no_fail(mock_engine_class, runner):
    mock_engine = MagicMock()
    mock_engine.check_stale.return_value = {"src1": True}
    mock_entry = MagicMock()
    mock_entry.last_sync = "2023-01-01"
    mock_engine.manifest.entries = {"src1": mock_entry}
    mock_engine_class.return_value = mock_engine

    result = runner.invoke(ci, ['check-standards'])
    assert result.exit_code == 0
    assert "Stale standards detected" in result.output

@patch('src.cli.commands.ci.StandardsSyncEngine')
def test_check_standards_stale_fail(mock_engine_class, runner):
    mock_engine = MagicMock()
    mock_engine.check_stale.return_value = {"src1": True}
    mock_entry = MagicMock()
    mock_entry.last_sync = "2023-01-01"
    mock_engine.manifest.entries = {"src1": mock_entry}
    mock_engine_class.return_value = mock_engine

    result = runner.invoke(ci, ['check-standards', '--fail-on-stale'])
    assert result.exit_code == 2
    assert "Stale standards detected" in result.output

def test_comment_file_read_error(runner, tmp_path):
    f = tmp_path / "test.txt"
    f.mkdir() # make it a directory to trigger read error
    result = runner.invoke(ci, ['comment', '--repo', 'owner/repo', '--pr', '1', '--file', str(f)])
    assert result.exit_code == 1
    assert "Error reading file" in result.output

def test_report_file_read_error(runner, tmp_path):
    f = tmp_path / "test.json"
    f.write_text("{invalid json}")
    result = runner.invoke(ci, ['report', '--scan-results', str(f), '--repo', 'owner/repo', '--pr', '1'])
    assert result.exit_code == 1
    assert "Error reading scan results" in result.output
