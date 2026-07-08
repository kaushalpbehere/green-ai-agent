"""
Configuration loader for Green-AI.

Loads and validates .green-ai.yaml configuration files with support for:
- Rule enable/disable per rule
- Standard selection
- Language configuration
"""
from src.utils.logger import logger

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

try:
    import httpx
except ImportError:
    httpx = None


class ConfigError(Exception):
    """Configuration loading/validation error."""


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
        'languages': ['python', 'javascript', 'typescript', 'java', 'go'],
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
                'formatted_print',
            ],
            'disabled': []
        },
        'standards': [],
        'ignore_files': ['*.pyc', '__pycache__', '.git', '.venv', 'node_modules'],
        'llm': {
            'provider': 'openai',
            'rate_limit': {
                'tpm': 10000,
                'rpm': 500
            }
        }
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

    def _is_url(self, path: str) -> bool:
        """Check if path is a URL."""
        return path.startswith('http://') or path.startswith('https://')

    def _fetch_remote_config(self, url: str) -> str:
        """
        Fetch remote config from URL and cache it.

        Args:
            url: URL to fetch

        Returns:
            Path to cached config file

        Raises:
            ConfigError: If fetch fails
        """
        if not httpx:
            raise ConfigError("httpx not installed. Cannot fetch remote config.")

        # Create cache directory
        cache_dir = Path.home() / '.green-ai' / 'remote_configs'
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Hash URL for filename
        url_hash = hashlib.md5(url.encode('utf-8'), usedforsecurity=False).hexdigest()
        cache_file = cache_dir / f"{url_hash}.yaml"

        # Cache lookup: use cached file if present. Smarter TTL/ETag caching
        # is tracked as ENG-016 in docs/backlog.md.
        if cache_file.exists():
            return str(cache_file)

        try:
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()

            with open(cache_file, 'w') as f:
                f.write(response.text)

            return str(cache_file)
        except Exception as e:
            raise ConfigError(f"Failed to fetch remote config from {url}: {e}")

    def _find_global_config_file(self) -> Optional[str]:
        """Find global configuration file in home or XDG directory."""
        home = Path.home()

        # Check ~/.green-ai.yaml
        global_config = home / '.green-ai.yaml'
        if global_config.exists():
            return str(global_config)

        # Check XDG_CONFIG_HOME
        xdg_home = os.environ.get('XDG_CONFIG_HOME', str(home / '.config'))
        xdg_config = Path(xdg_home) / 'green-ai' / 'config.yaml'
        if xdg_config.exists():
            return str(xdg_config)

        return None

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file or defaults.

        Returns:
            Configuration dictionary

        Raises:
            ConfigError: If YAML is invalid or required field missing
        """
        # Start with defaults
        config = self.DEFAULT_CONFIG.copy()

        # Import yaml when needed
        try:
            import yaml
        except ImportError:
            raise ConfigError(
                "PyYAML not installed. Install with: pip install pyyaml\n"
                "Or remove .green-ai.yaml to use defaults."
            )

        # 1. Load Database Config (Global Engine Defaults)
        db_config = self._fetch_db_config("GLOBAL")
        config = self._merge_config(config, db_config)

        # 2. Load Organization Config (from DB, if org_id is present)
        # Note: Org ID would typically be injected via environment or API context
        org_id = os.environ.get("GREEN_AI_ORG_ID")
        if org_id:
            org_config = self._fetch_db_config(f"ORG_{org_id}")
            config = self._merge_config(config, org_config)

        # 3. Load Project Config (from DB, if project_id is present)
        project_id = os.environ.get("GREEN_AI_PROJECT_ID")
        if project_id:
            project_config = self._fetch_db_config(f"PROJECT_{project_id}")
            config = self._merge_config(config, project_config)

        # 4. Load Global Config (User home dir, merged into DB hierarchy)
        global_path = self._find_global_config_file()
        if global_path:
            try:
                with open(global_path, 'r') as f:
                    global_conf = yaml.safe_load(f) or {}
                config = self._merge_config(config, global_conf)
            except Exception as e:
                # Silently ignore global config errors to avoid breaking execution
                logger.warning(f"Failed to load global config: {e}")

        # 5. Load Local Config (merged into defaults+DB+global)
        local_config_path = self.config_path

        if local_config_path and self._is_url(local_config_path):
            try:
                local_config_path = self._fetch_remote_config(local_config_path)
            except ConfigError as e:
                # If remote fetch fails, we re-raise it
                raise e

        if local_config_path and os.path.exists(local_config_path):
            try:
                with open(local_config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                config = self._merge_config(config, file_config)
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in {local_config_path}: {e}")
            except IOError as e:
                raise ConfigError(f"Cannot read {local_config_path}: {e}")

        # Validate using Pydantic
        self.config = self._validate_config(config)

        return self.config

    def _fetch_db_config(self, scope: str) -> Dict:
        """
        Stub to fetch rules and overrides from the DB schema created in IMPL-001.
        In a full implementation, this connects to the SQLAlchemy session
        and queries RuleOverride joined with RuleDefinition.
        """
        # Return an empty dict stub for now until full DB session injection is built
        return {}

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config into defaults."""
        from src.utils.dict_utils import deep_merge
        return deep_merge(default, user)

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration using Pydantic model.

        Raises:
            ConfigError: If validation fails
        """
        try:
            from src.core.config_models import GreenAIConfig
            model = GreenAIConfig(**config)
            return model.model_dump()
        except ImportError:
            raise ConfigError("Pydantic not installed or config_models missing.")
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}")

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

    def get_rule_severity(self, rule_id: str, default_severity: str = "medium") -> str:
        """
        Get rule severity with overrides.

        Args:
            rule_id: Rule ID to check
            default_severity: Default severity if not overridden

        Returns:
            Severity string (e.g. 'critical', 'major')
        """
        if not self.config:
            self.load()

        # Get rules dictionary safely
        rules_config = self.config.get('rules', {})
        if not isinstance(rules_config, dict):
            return default_severity

        severity_map = rules_config.get('severity', {})
        if not severity_map or not isinstance(severity_map, dict):
            return default_severity

        return severity_map.get(rule_id, default_severity)

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
