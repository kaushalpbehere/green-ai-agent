"""
Configuration loader for Green-AI.

Loads and validates .green-ai.yaml configuration files with support for:
- Rule enable/disable per rule
- Standard selection
- Language configuration
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigError(Exception):
    """Configuration loading/validation error."""
    pass


class ConfigLoader:
    """
    Loads and validates .green-ai.yaml configuration files.
    
    Features:
    - Load from project root
    - YAML validation against schema
    - Fall back to defaults if file doesn't exist
    - CLI override support
    
    Example config:
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
          - ecocode_python
    """
    
    # Default configuration (works if no .green-ai.yaml exists)
    DEFAULT_CONFIG = {
        'languages': ['python', 'javascript'],
        'rules': {
            'enabled': [
                'excessive_nesting_depth',
                'unnecessary_computation',
                'inefficient_memory_operation',
                'io_in_loop',
                'unused_variables',
                'unused_imports',
                'proper_resource_cleanup',
                'quadratic_algorithm',
                'dead_code_block',
                'blocking_io',
                'high_cyclomatic_complexity',
                'string_concatenation_in_loop',
                'exceptions_in_loop',
                'inefficient_data_structure',
                'large_constant_allocation',
                'no_infinite_loops',
                'inefficient_loop',
                'excessive_logging',
                'magic_numbers',
                'no_n2_algorithms',
                'synchronous_io',
                'excessive_console_logging',
                'heavy_object_copy',
                'process_spawning',
                'inefficient_file_read',
                'global_variable_mutation',
                'pandas_iterrows',
                'string_concatenation',
                'unnecessary_dom_manipulation',
                'eval_usage',
                'setInterval_animation',
                'momentjs_deprecated',
                'document_write',
                'alert_usage',
            ],
            'disabled': []
        },
        'standards': [],
        'ignore_files': ['*.pyc', '__pycache__', '.git', '.venv', 'node_modules']
    }
    
    # Configuration schema definition
    SCHEMA = {
        'languages': (list, ['python', 'javascript']),
        'rules': (dict, {
            'enabled': (list, []),
            'disabled': (list, [])
        }),
        'standards': (list, []),
        'ignore_files': (list, []),
        'auto_fix': (bool, False),
        'llm_provider': (str, None),
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to .green-ai.yaml file. If None, searches project root.
        """
        self.config_path = config_path or self._find_config_file()
        self.config: Dict[str, Any] = {}
    
    def _find_config_file(self) -> Optional[str]:
        """Find .green-ai.yaml in current directory or parent directories."""
        current = Path.cwd()
        
        # Search up to 5 levels
        for _ in range(5):
            config_file = current / '.green-ai.yaml'
            if config_file.exists():
                return str(config_file)
            
            # Go to parent
            if current.parent == current:
                break
            current = current.parent
        
        return None
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or defaults.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigError: If YAML is invalid or required field missing
        """
        if not self.config_path or not os.path.exists(self.config_path):
            # No config file found, use defaults
            self.config = self.DEFAULT_CONFIG.copy()
            return self.config
        
        # Import yaml when needed
        try:
            import yaml
        except ImportError:
            raise ConfigError(
                "PyYAML not installed. Install with: pip install pyyaml\n"
                "Or remove .green-ai.yaml to use defaults."
            )
        
        # Load YAML file
        try:
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {self.config_path}: {e}")
        except IOError as e:
            raise ConfigError(f"Cannot read {self.config_path}: {e}")
        
        # Merge with defaults (user config overrides defaults)
        self.config = self._merge_config(self.DEFAULT_CONFIG.copy(), file_config)
        
        # Validate
        self._validate_config(self.config)
        
        return self.config
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config into defaults."""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration against schema.
        
        Raises:
            ConfigError: If validation fails
        """
        errors = []
        
        for key, (expected_type, default) in self.SCHEMA.items():
            if key not in config:
                config[key] = default
                continue
            
            value = config[key]
            
            # Check type
            if not isinstance(value, expected_type):
                errors.append(
                    f"{key}: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
        
        # Validate nested structures
        if 'rules' in config and isinstance(config['rules'], dict):
            if 'enabled' not in config['rules']:
                config['rules']['enabled'] = []
            if 'disabled' not in config['rules']:
                config['rules']['disabled'] = []
            
            if not isinstance(config['rules']['enabled'], list):
                errors.append("rules.enabled must be a list")
            if not isinstance(config['rules']['disabled'], list):
                errors.append("rules.disabled must be a list")
        
        if errors:
            error_msg = "Configuration validation failed:\n"
            error_msg += "\n".join(f"  - {e}" for e in errors)
            raise ConfigError(error_msg)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation: 'rules.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        if not self.config:
            self.load()
        
        # Support dot notation (e.g., 'rules.enabled')
        if '.' in key:
            parts = key.split('.')
            value = self.config
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return default
            return value if value is not None else default
        
        return self.config.get(key, default)
    
    def is_rule_enabled(self, rule_id: str) -> bool:
        """
        Check if a rule is enabled.
        
        Args:
            rule_id: Rule ID to check
            
        Returns:
            True if rule is enabled, False if disabled
        """
        if not self.config:
            self.load()
        
        enabled = self.get('rules.enabled', [])
        disabled = self.get('rules.disabled', [])
        
        # If rule is explicitly disabled, it's disabled
        if rule_id in disabled:
            return False
        
        # If rule is explicitly enabled, it's enabled
        if rule_id in enabled:
            return True
        
        # Default: enabled (for backward compatibility)
        return True
    
    def get_enabled_languages(self) -> List[str]:
        """Get list of enabled languages."""
        if not self.config:
            self.load()
        return self.get('languages', ['python', 'javascript'])
    
    def get_ignored_files(self) -> List[str]:
        """Get list of file patterns to ignore."""
        if not self.config:
            self.load()
        return self.get('ignore_files', [])
    
    def export_example_yaml(self, output_path: str) -> None:
        """
        Export example .green-ai.yaml file.
        
        Args:
            output_path: Path where to write the example file
        """
        try:
            import yaml
        except ImportError:
            raise ConfigError(
                "PyYAML not installed. Install with: pip install pyyaml"
            )
        
        example_config = {
            'languages': ['python', 'javascript'],
            'rules': {
                'enabled': [
                    'excessive_nesting_depth',
                    'io_in_loop',
                    'resource_leak_file',
                    'quadratic_algorithm',
                ],
                'disabled': [
                    'unused_variable',  # Example: disable if too noisy
                ]
            },
            'standards': [
                'gsf_principles',
                'ecocode_python',
            ],
            'ignore_files': [
                '*.pyc',
                '__pycache__',
                '.git',
                '.venv',
                'node_modules',
                'dist',
                'build',
            ],
            'auto_fix': False,
        }
        
        with open(output_path, 'w') as f:
            f.write("# Green-AI Configuration\n")
            f.write("# Copy this file to .green-ai.yaml in your project root\n")
            f.write("# All fields are optional and have sensible defaults\n\n")
            yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Example configuration written to: {output_path}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_path: Optional path to .green-ai.yaml
        
    Returns:
        Configuration dictionary
    """
    loader = ConfigLoader(config_path)
    return loader.load()
