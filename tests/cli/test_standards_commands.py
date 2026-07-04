import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.commands.standards import standards_list, standards_enable, standards_disable, standards_update, standards_export

def test_standards_list():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsRegistry') as MockRegistry:
        mock_registry = MockRegistry.return_value
        mock_registry.list_standards.return_value = {
            'test_std': {'enabled': True, 'rule_count': 10, 'languages': ['python']}
        }

        result = runner.invoke(standards_list)

        assert result.exit_code == 0
        assert "TEST_STD [ENABLED]" in result.output
        assert "Rules: 10" in result.output

def test_standards_enable():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsRegistry') as MockRegistry:
        mock_registry = MockRegistry.return_value

        result = runner.invoke(standards_enable, ['test_std'])

        assert result.exit_code == 0
        assert "Standard 'test_std' enabled" in result.output
        mock_registry.enable_standard.assert_called_once_with('test_std')

def test_standards_disable():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsRegistry') as MockRegistry:
        mock_registry = MockRegistry.return_value

        result = runner.invoke(standards_disable, ['test_std'])

        assert result.exit_code == 0
        assert "Standard 'test_std' disabled" in result.output
        mock_registry.disable_standard.assert_called_once_with('test_std')

def test_standards_update():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsRegistry') as MockRegistry:
        mock_registry = MockRegistry.return_value
        mock_registry.sync_standards.return_value = {'test_std': True}

        result = runner.invoke(standards_update)

        assert result.exit_code == 0
        assert "Standards updated from online sources" in result.output
        assert "test_std: [OK]" in result.output

def test_standards_export():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsRegistry') as MockRegistry:
        mock_registry = MockRegistry.return_value
        mock_registry.export_rules_json.return_value = '{"rules": []}'

        result = runner.invoke(standards_export)

        assert result.exit_code == 0
        assert '{"rules": []}' in result.output
        mock_registry.export_rules_json.assert_called_once()

from src.cli.commands.standards import standards_sync, standards_versions, standards_check, standards_diff

def test_standards_sync():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        mock_engine = MockEngine.return_value
        class MockEntry:
            def __init__(self):
                self.sync_ok = True
                self.display_name = 'Test Std'
                self.version_tag = 'v1.0'
                self.content_hash = '1234567890abcdef'
                self.size_bytes = 1024
                self.last_sync = '2023-01-01'

        mock_engine.sync_all.return_value = {'test_std': MockEntry()}

        result = runner.invoke(standards_sync)

        assert result.exit_code == 0
        assert "Standards Sync Results" in result.output
        assert "Test Std" in result.output
        assert "version : v1.0" in result.output

def test_standards_versions():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        mock_engine = MockEngine.return_value
        mock_engine.versions.return_value = [
            {'name': 'test_std', 'display_name': 'Test Std', 'version_tag': 'v1.0', 'content_hash': '1234567890abcdef', 'sync_ok': True, 'last_sync': '2023-01-01'}
        ]

        result = runner.invoke(standards_versions)

        assert result.exit_code == 0
        assert "Standards Version Manifest" in result.output
        assert "test_std" in result.output
        assert "Test Std" in result.output

def test_standards_check():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        mock_engine = MockEngine.return_value
        mock_engine.check_stale.return_value = {'test_std': False}
        class MockEntry:
            last_sync = '2023-01-01'
        mock_engine.manifest.entries = {'test_std': MockEntry()}

        result = runner.invoke(standards_check)

        assert result.exit_code == 0
        assert "Standards Freshness Check" in result.output
        assert "All standards are fresh." in result.output

import hashlib
hash_old_content = hashlib.sha256(b"old content").hexdigest()

def test_standards_diff():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        mock_engine = MockEngine.return_value

        # Test unknown source
        result = runner.invoke(standards_diff, ['unknown'])
        assert result.exit_code == 1
        assert "Unknown source" in result.output

        # Test known source but no cache
        mock_engine.get_cached.return_value = None
        result = runner.invoke(standards_diff, ['gsf'])
        assert result.exit_code == 1
        assert "No cached version" in result.output

def test_standards_diff_success():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        with patch('requests.get') as mock_get:
            mock_engine = MockEngine.return_value
            mock_engine.get_cached.return_value = b"old content"
            class MockEntry:
                def __init__(self):
                    self.content_hash = hash_old_content
                    self.size_bytes = 10
                    self.version_tag = "v1"
                    self.last_sync = "today"
            mock_engine.manifest.entries = {'gsf': MockEntry()}

            mock_resp = MagicMock()
            mock_resp.content = b"old content"
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(standards_diff, ['gsf'])
            assert result.exit_code == 0
            assert "No changes" in result.output

def test_standards_diff_changed():
    runner = CliRunner()
    with patch('src.cli.commands.standards.StandardsSyncEngine') as MockEngine:
        with patch('requests.get') as mock_get:
            mock_engine = MockEngine.return_value
            mock_engine.get_cached.return_value = b"old content"
            class MockEntry:
                def __init__(self):
                    self.content_hash = hash_old_content
                    self.size_bytes = 10
                    self.version_tag = "v1"
                    self.last_sync = "today"
            mock_engine.manifest.entries = {'gsf': MockEntry()}

            mock_resp = MagicMock()
            mock_resp.content = b"new content here"
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(standards_diff, ['gsf'])
            assert result.exit_code == 0
            assert "Remote has new content" in result.output
