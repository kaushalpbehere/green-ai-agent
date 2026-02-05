"""
Unit tests for AI Suggester module
"""

import pytest
from src.core.fixer import AISuggester

def test_ai_suggester_init():
    suggester = AISuggester()
    assert suggester is not None

def test_suggest_fix():
    suggester = AISuggester()
    issue = {'id': 'inefficient_loop', 'type': 'green_violation'}
    suggestion = suggester.suggest_fix(issue)
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_suggest_fix_empty():
    suggester = AISuggester()
    suggestion = suggester.suggest_fix({})
    assert isinstance(suggestion, str)