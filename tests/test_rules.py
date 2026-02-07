"""
Unit tests for Rules module
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.rules import RuleRepository

def test_rule_repository_init():
    repo = RuleRepository()
    assert hasattr(repo, 'rules')

def test_get_rules_python():
    repo = RuleRepository()
    rules = repo.get_rules('python')
    assert isinstance(rules, list)
    assert len(rules) > 0
    for rule in rules:
        assert 'id' in rule
        assert 'pattern' in rule
        assert 'description' in rule
        assert 'severity' in rule

def test_get_rules_javascript():
    repo = RuleRepository()
    rules = repo.get_rules('javascript')
    assert isinstance(rules, list)
    # May be empty or have rules

def test_get_rules_unknown():
    repo = RuleRepository()
    rules = repo.get_rules('unknown')
    assert isinstance(rules, list)
    # Probably empty