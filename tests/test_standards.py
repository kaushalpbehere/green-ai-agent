"""
Tests for Standards Registry and Manager
"""

import pytest
import os
import tempfile
from src.standards.registry import StandardsRegistry, StandardRule


class TestStandardsRegistry:
    def test_registry_init(self):
        registry = StandardsRegistry()
        assert registry is not None
        assert len(registry.standards) > 0
    
    def test_list_standards(self):
        registry = StandardsRegistry()
        standards = registry.list_standards()
        assert 'gsf' in standards
        assert 'ecocode' in standards
        assert 'microsoft' in standards
    
    def test_enabled_standards_by_default(self):
        registry = StandardsRegistry()
        standards = registry.list_standards()
        # All standards should be enabled by default
        assert all(s['enabled'] for s in standards.values())
    
    def test_enable_disable_standard(self):
        registry = StandardsRegistry()
        registry.disable_standard('gsf')
        assert 'gsf' not in registry.enabled_standards
        
        registry.enable_standard('gsf')
        assert 'gsf' in registry.enabled_standards
    
    def test_get_enabled_rules_python(self):
        # Use dummy config to ensure default rules are enabled
        registry = StandardsRegistry(config_path="nonexistent.yaml")
        rules = registry.get_enabled_rules('python')
        assert len(rules) > 0
        # All rules should support python
        for rule in rules:
            assert 'python' in [l.lower() for l in rule.languages]
    
    def test_get_enabled_rules_javascript(self):
        # Use dummy config to ensure default rules are enabled
        registry = StandardsRegistry(config_path="nonexistent.yaml")
        rules = registry.get_enabled_rules('javascript')
        assert len(rules) > 0
    
    def test_disable_rule(self):
        # Use dummy config to ensure default rules are enabled
        registry = StandardsRegistry(config_path="nonexistent.yaml")
        # Get rules for a specific language to test filtering
        python_rules_before = registry.get_enabled_rules('python')
        initial_count = len(python_rules_before)
        
        if initial_count > 0:
            rule_id = python_rules_before[0].id
            registry.disable_rule(rule_id)
            assert rule_id in registry.disabled_rules
            
            # When rule is disabled, get_enabled_rules should return fewer rules
            python_rules_after = registry.get_enabled_rules('python')
            # The disabled rule should not be in the list anymore
            disabled_found = any(r.id == rule_id for r in python_rules_after)
            assert not disabled_found
    
    def test_export_rules_json(self):
        registry = StandardsRegistry()
        json_output = registry.export_rules_json()
        assert json_output is not None
        assert '[' in json_output
        assert 'id' in json_output
    
    def test_export_rules_yaml(self):
        registry = StandardsRegistry()
        yaml_output = registry.export_rules_yaml()
        assert yaml_output is not None
        assert 'id:' in yaml_output or 'name:' in yaml_output
    
    def test_standard_rule_dataclass(self):
        rule = StandardRule(
            id='test_rule',
            name='Test Rule',
            description='A test rule',
            severity='major',
            languages=['python'],
            pattern='test.*',
            remediation='Fix it',
            source='test'
        )
        assert rule.id == 'test_rule'
        assert rule.severity == 'major'
    
    def test_sync_standards(self):
        registry = StandardsRegistry()
        result = registry.sync_standards()
        assert isinstance(result, dict)
        # Should return all standards
        assert len(result) >= 5


class TestStandardsIntegration:
    def test_config_persistence(self):
        """Test that standard settings persist in config file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, '.green-ai.yaml')
            
            # Create first registry instance
            registry1 = StandardsRegistry(config_path=config_file)
            registry1.disable_standard('gsf')
            registry1._save_config()
            
            # Create second registry instance and verify setting persists
            registry2 = StandardsRegistry(config_path=config_file)
            assert 'gsf' not in registry2.enabled_standards
