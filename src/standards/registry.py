"""
Standards Registry and Manager
Manages loading, enabling, disabling, and syncing green coding standards from multiple sources
"""

import os
import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional
from pathlib import Path


@dataclass
class StandardRule:
    """Represents a single rule from a standard"""
    id: str
    name: str
    description: str
    severity: str  # critical, major, minor
    languages: List[str]
    pattern: str  # Regex or description
    remediation: str
    source: str  # GSF, ecoCode, SUSCOM, etc.


class StandardsRegistry:
    """Manages all available standards and their rules"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '.green-ai.yaml'
        )
        self.standards: Dict[str, List[StandardRule]] = {}
        self.enabled_standards: Set[str] = set()
        self.disabled_rules: Set[str] = set()
        self.enabled_custom_rules: Set[str] = set()
        
        self._load_defaults()
        self._load_config()
    
    def _load_defaults(self):
        """Load default standards from built-in definitions"""
        # GSF Standards
        self.standards['gsf'] = [
            StandardRule(
                id='no_infinite_loops',
                name='No Infinite Loops',
                description='Infinite loops consume unlimited energy',
                severity='critical',
                languages=['python', 'javascript', 'java', 'go', 'rust', 'cpp', 'csharp'],
                pattern=r'while\s*\(\s*[Tt]rue\s*\)',
                remediation='Add loop termination conditions',
                source='GSF'
            ),
            StandardRule(
                id='no_n2_algorithms',
                name='No O(n²) Algorithms',
                description='Nested loops without optimization waste energy',
                severity='critical',
                languages=['python', 'javascript', 'java', 'go', 'rust'],
                pattern=r'for.*for\s*(',
                remediation='Use efficient algorithms or vectorization',
                source='GSF'
            ),
            StandardRule(
                id='proper_resource_cleanup',
                name='Proper Resource Cleanup',
                description='Always close files, connections, and resources',
                severity='major',
                languages=['python', 'javascript', 'java'],
                pattern=r'open\s*\(',
                remediation='Use context managers (with statement)',
                source='GSF'
            ),
        ]
        
        # ecoCode Standards
        self.standards['ecocode'] = [
            StandardRule(
                id='inefficient_loop',
                name='Inefficient Loop Detection',
                description='Detects non-optimized loops that could be vectorized',
                severity='major',
                languages=['python', 'javascript', 'java'],
                pattern=r'for\s+\w+\s+in\s+range\(',
                remediation='Consider list comprehension or vectorization',
                source='ecoCode'
            ),
            StandardRule(
                id='unnecessary_computation',
                name='Unnecessary Computation',
                description='Redundant calculations in loops',
                severity='major',
                languages=['python', 'javascript'],
                pattern=r'',
                remediation='Cache or optimize computation placement',
                source='ecoCode'
            ),
        ]
        
        # SUSCOM Standards
        self.standards['suscom'] = [
            StandardRule(
                id='algorithm_efficiency',
                name='Algorithm Efficiency',
                description='Choose efficient algorithms for the problem',
                severity='major',
                languages=['python', 'javascript', 'java', 'go', 'rust'],
                pattern=r'',
                remediation='Profile and optimize algorithm complexity',
                source='SUSCOM'
            ),
        ]
        
        # NVIDIA Standards
        self.standards['nvidia'] = [
            StandardRule(
                id='gpu_utilization',
                name='GPU Utilization Check',
                description='Ensure proper GPU memory management',
                severity='major',
                languages=['python', 'cuda'],
                pattern=r'',
                remediation='Optimize GPU memory allocation and transfer',
                source='NVIDIA'
            ),
        ]
        
        # Microsoft Standards
        self.standards['microsoft'] = [
            StandardRule(
                id='dotnet_optimization',
                name='.NET Memory Optimization',
                description='Reduce memory allocations in .NET code',
                severity='major',
                languages=['csharp', 'vbnet'],
                pattern=r'new\s+\w+\[',
                remediation='Use object pools or stackalloc',
                source='Microsoft'
            ),
        ]
        
        # All standards enabled by default
        self.enabled_standards = set(self.standards.keys())
    
    def _load_config(self):
        """Load user configuration if exists"""
        if not os.path.exists(self.config_path):
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            standards_config = config.get('standards', {})
            
            # Apply enabled/disabled standards
            if 'enabled' in standards_config:
                self.enabled_standards = set(standards_config['enabled'])
            if 'disabled' in standards_config:
                disabled = set(standards_config['disabled'])
                self.enabled_standards -= disabled
            
            # Apply disabled rules and custom rules
            rules_config = standards_config.get('rules', {})
            self.disabled_rules = set(rules_config.get('disable', []))
            self.enabled_custom_rules = set(rules_config.get('enable', []))
        
        except Exception as e:
            print(f"Warning: Could not load standards config: {e}")
    
    def get_enabled_rules(self, language: str) -> List[StandardRule]:
        """Get all enabled rules for a specific language"""
        rules = []
        
        for standard_name in self.enabled_standards:
            if standard_name in self.standards:
                for rule in self.standards[standard_name]:
                    if language.lower() in [l.lower() for l in rule.languages]:
                        if rule.id not in self.disabled_rules:
                            rules.append(rule)
        
        return rules
    
    def get_all_rules(self) -> List[StandardRule]:
        """Get all available rules from enabled standards"""
        rules = []
        for standard_name in self.enabled_standards:
            if standard_name in self.standards:
                rules.extend(self.standards[standard_name])
        return rules
    
    def enable_standard(self, standard_name: str):
        """Enable a standard"""
        if standard_name in self.standards:
            self.enabled_standards.add(standard_name)
            self._save_config()
    
    def disable_standard(self, standard_name: str):
        """Disable a standard"""
        self.enabled_standards.discard(standard_name)
        self._save_config()
    
    def disable_rule(self, rule_id: str):
        """Disable a specific rule"""
        self.disabled_rules.add(rule_id)
        self._save_config()
    
    def enable_rule(self, rule_id: str):
        """Enable a specific rule"""
        self.disabled_rules.discard(rule_id)
        self._save_config()
    
    def list_standards(self) -> Dict[str, Dict]:
        """List all available standards with metadata"""
        return {
            name: {
                'enabled': name in self.enabled_standards,
                'rule_count': len(rules),
                'languages': list(set(
                    lang for rule in rules for lang in rule.languages
                ))
            }
            for name, rules in self.standards.items()
        }
    
    def _save_config(self):
        """Save current configuration to YAML file"""
        config = {
            'standards': {
                'enabled': list(self.enabled_standards),
                'rules': {
                    'disable': list(self.disabled_rules),
                    'enable': list(self.enabled_custom_rules)
                }
            }
        }
        
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Could not save standards config: {e}")
    
    def sync_standards(self) -> Dict[str, bool]:
        """
        Sync standards from online sources (placeholder for future implementation)
        Returns dict of synced standards
        """
        # TODO: Implement fetching latest standards from GitHub repos
        # - GSF: https://github.com/Green-Software-Foundation/standards
        # - ecoCode: https://github.com/green-code-initiative/ecocode
        # - SUSCOM: https://suscom.io/standards
        return {name: True for name in self.standards.keys()}
    
    def export_rules_json(self) -> str:
        """Export enabled rules as JSON"""
        rules = self.get_all_rules()
        return json.dumps([asdict(rule) for rule in rules], indent=2)
    
    def export_rules_yaml(self) -> str:
        """Export enabled rules as YAML"""
        rules = self.get_all_rules()
        return yaml.dump([asdict(rule) for rule in rules], default_flow_style=False)
