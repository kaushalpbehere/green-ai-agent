"""
Tests for configuration system.
"""

import os
import pytest
import tempfile
from pathlib import Path
from src.core.config import ConfigLoader, ConfigError


class TestConfigLoader:
    """Test ConfigLoader functionality."""
    
    def test_default_config_when_no_file_exists(self):
        """Test that default config is used when no file exists."""
        loader = ConfigLoader('/nonexistent/path/.green-ai.yaml')
        config = loader.load()
        
        assert config is not None
        assert 'languages' in config
        assert 'python' in config['languages']
        assert 'rules' in config
    
    def test_load_valid_yaml_config(self):
        """Test loading a valid YAML configuration."""
        yaml_content = """
languages:
  - python
  - javascript

rules:
  enabled:
    - excessive_nesting_depth
    - io_in_loop
  disabled:
    - unused_variable

standards:
  - gsf_principles
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            config = loader.load()
            
            assert config['languages'] == ['python', 'javascript']
            assert 'excessive_nesting_depth' in config['rules']['enabled']
            assert 'unused_variable' in config['rules']['disabled']
            assert 'gsf_principles' in config['standards']
        finally:
            os.unlink(temp_path)
    
    def test_config_merges_with_defaults(self):
        """Test that config merges with defaults (user overrides)."""
        yaml_content = """
languages:
  - python
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            config = loader.load()
            
            # User-specified language
            assert config['languages'] == ['python']
            
            # Default rules should be present
            assert 'rules' in config
            assert 'enabled' in config['rules']
        finally:
            os.unlink(temp_path)
    
    def test_is_rule_enabled(self):
        """Test rule enabled/disabled checking."""
        yaml_content = """
rules:
  enabled:
    - excessive_nesting_depth
  disabled:
    - unused_variable
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            loader.load()
            
            # Explicitly enabled
            assert loader.is_rule_enabled('excessive_nesting_depth') is True
            
            # Explicitly disabled
            assert loader.is_rule_enabled('unused_variable') is False
            
            # Default (not listed) should be enabled
            assert loader.is_rule_enabled('io_in_loop') is True
        finally:
            os.unlink(temp_path)
    
    def test_get_with_dot_notation(self):
        """Test getting nested values with dot notation."""
        yaml_content = """
rules:
  enabled:
    - rule1
    - rule2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            loader.load()
            
            enabled = loader.get('rules.enabled')
            assert enabled == ['rule1', 'rule2']
            
            # Test default value
            missing = loader.get('nonexistent.key', 'default')
            assert missing == 'default'
        finally:
            os.unlink(temp_path)
    
    def test_get_enabled_languages(self):
        """Test getting enabled languages from config."""
        yaml_content = """
languages:
  - python
  - typescript
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            loader.load()
            
            languages = loader.get_enabled_languages()
            assert 'python' in languages
            assert 'typescript' in languages
        finally:
            os.unlink(temp_path)
    
    def test_validation_errors(self):
        """Test configuration validation errors."""
        yaml_content = """
languages: "not_a_list"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            # Invalid config should raise ConfigError
            with pytest.raises(ConfigError):
                config = loader.load()
        finally:
            os.unlink(temp_path)


class TestConfigIntegration:
    """Test config integration with scanner."""
    
    def test_scanner_respects_config(self):
        """Test that scanner respects configuration."""
        from src.core.scanner import Scanner
        
        yaml_content = """
languages:
  - python

rules:
  disabled:
    - unused_variable
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Create scanner with config
            scanner = Scanner(config_path=temp_path)
            
            # Check that config is loaded
            assert scanner.config_loader.is_rule_enabled('excessive_nesting_depth') is True
            assert scanner.config_loader.is_rule_enabled('unused_variable') is False
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
