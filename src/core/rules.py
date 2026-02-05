"""
Green Software Rules Repository

TIER 1: Critical Carbon Footprint Rules (40-60% energy waste)
  - Nested loops (3+ levels): Exponential complexity
  - Unnecessary computations: Wasted CPU cycles
  - Memory inefficiency: High energy operations
  - I/O in loops: Expensive repeated disk/network access
  
TIER 2: Code Quality & Performance (25-35% energy waste)
  - Unused variables/imports: Memory overhead
  - Resource leaks: Persistent memory consumption
  - Algorithm complexity: O(n²) patterns
  - Redundant operations: Repeated work
"""

import json
import os
import yaml
from pathlib import Path
from src.utils.logger import logger

class RuleRepository:
    def __init__(self, rules_dir: str = None):
        """
        Initialize RuleRepository.
        
        Args:
            rules_dir: Directory containing YAML rules. Defaults to 'rules' in project root.
        """
        if rules_dir:
            self.rules_dir = Path(rules_dir)
        else:
            # Default to rules/ in project root
            self.rules_dir = Path(__file__).parent.parent.parent / 'rules'
            
        self.rules = self._load_rules_from_yaml()
    
    def _load_rules_from_yaml(self):
        """
        Load rules dynamically from YAML files in the rules directory.
        """
        rules_by_lang = {}
        
        if not self.rules_dir.exists():
            logger.error(f"Rules directory not found: {self.rules_dir}")
            return {}
            
        logger.info(f"Loading rules from {self.rules_dir}")
        
        for yaml_file in self.rules_dir.glob('*.yaml'):
            lang = yaml_file.stem
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'rules' in data:
                        rules_by_lang[lang] = data['rules']
                        logger.info(f"Loaded {len(data['rules'])} rules for {lang}")
            except Exception as e:
                logger.error(f"Failed to load rules from {yaml_file}: {e}")
                
        return rules_by_lang
    
    def get_rules(self, language):
        """Get all rules for a language."""
        return self.rules.get(language, [])
    
    def get_rule(self, language, rule_id):
        """Get a specific rule by ID."""
        rules = self.get_rules(language)
        for rule in rules:
            if rule['id'] == rule_id:
                return rule
        return None
    
    def get_rules_by_severity(self, language, severity):
        """Get all rules of a specific severity."""
        rules = self.get_rules(language)
        return [r for r in rules if r['severity'] == severity]
    
    def get_rules_by_tag(self, language, tag):
        """Get all rules with a specific tag."""
        rules = self.get_rules(language)
        return [r for r in rules if tag in r.get('tags', [])]
    
    def add_rule(self, language, rule):
        """Add a custom rule (in-memory only)."""
        if language not in self.rules:
            self.rules[language] = []
        self.rules[language].append(rule)
    
    def export_rules_json(self, language=None):
        """Export rules as JSON."""
        rules_to_export = self.rules if language is None else {language: self.rules.get(language, [])}
        return json.dumps(rules_to_export, indent=2)
    
    def export_rules_yaml(self, language=None):
        """Export rules as YAML format string."""
        rules_to_export = self.rules if language is None else {language: self.rules.get(language, [])}
        return yaml.dump({'rules': rules_to_export}, default_flow_style=False)
    
    def update_from_source(self):
        """Reload rules from disk."""
        self.rules = self._load_rules_from_yaml()
