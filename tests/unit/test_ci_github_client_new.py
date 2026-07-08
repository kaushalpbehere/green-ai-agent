import pytest
from unittest.mock import patch, MagicMock
from src.core.ci.github_client import GitHubClient

def test_init_with_token():
    client = GitHubClient(token="test_token")
    assert client.token == "test_token"
    assert client.headers["Authorization"] == "Bearer test_token"

@patch('os.getenv', return_value="env_token")
def test_init_with_env(mock_getenv):
    client = GitHubClient()
    assert client.token == "env_token"

@patch('os.getenv', return_value=None)
def test_init_no_token(mock_getenv):
    with pytest.raises(ValueError):
        GitHubClient()

@patch('httpx.Client.post')
def test_post_comment(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 123}
    mock_post.return_value = mock_response

    client = GitHubClient(token="test")
    res = client.post_comment("owner", "repo", 1, "body")
    assert res == {"id": 123}
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.github.com/repos/owner/repo/issues/1/comments"
    assert kwargs["json"] == {"body": "body"}

@patch('httpx.Client.get')
def test_get_pr_diff(mock_get):
    mock_response = MagicMock()
    mock_response.text = "diff"
    mock_get.return_value = mock_response

    client = GitHubClient(token="test")
    res = client.get_pr_diff("owner", "repo", 1)
    assert res == "diff"
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.github.com/repos/owner/repo/pulls/1"
    assert kwargs["headers"]["Accept"] == "application/vnd.github.v3.diff"

def test_parse_diff_normal():
    client = GitHubClient(token="test")
    diff_text = """diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -10,3 +10,4 @@
 context
+added 1
+added 2
-removed
 context"""
    changes = client.parse_diff(diff_text)
    assert 'test.py' in changes
    assert changes['test.py'] == {11, 12}

def test_parse_diff_single_line():
    client = GitHubClient(token="test")
    diff_text = """+++ b/file.py
@@ -1 +1 @@
+new_line
"""
    changes = client.parse_diff(diff_text)
    assert changes['file.py'] == {1}

def test_parse_diff_bad_header():
    client = GitHubClient(token="test")
    diff_text = """+++ b/file.py
@@ invalid @@
+new_line
"""
    changes = client.parse_diff(diff_text)
    assert changes['file.py'] == {0}

def test_parse_diff_no_file():
    client = GitHubClient(token="test")
    diff_text = """@@ -1,1 +1,1 @@
+new_line
"""
    changes = client.parse_diff(diff_text)
    assert changes == {}
