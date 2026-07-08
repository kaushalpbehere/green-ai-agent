from src.utils.logger import logger
from typing import Dict, Any, List, Optional
import ast
from datetime import datetime, timezone
from src.core.remediation.engine import RemediationEngine
from src.core.analyzer import EmissionAnalyzer
from src.core.detectors import detect_violations
from src.core.detectors.ai_usage_detector import scan_file_for_ai_usage
from src.core.cache import DiskCache
from src.core.scanner.suppression import get_suppressions, is_suppressed, load_external_suppressions
import os

_disk_cache_instance = None


def _checks_include(config: Dict, check: str) -> bool:
    if not config:
        return check != 'ai'
    checks = config.get('checks', ['all'])
    if isinstance(checks, str):
        checks = [checks]
    return 'all' in checks or check in checks


def _get_git_blame_info(file_path: str, lines: List[int]) -> Dict[int, Dict[str, str]]:
    """Fetch git blame info for specific lines using pygit2 for high performance."""
    blame_info = {}
    if not lines:
        return blame_info

    try:
        import pygit2
    except ImportError:
        return blame_info

    try:
        repo_path = pygit2.discover_repository(file_path)
        if not repo_path:
            return blame_info

        repo = pygit2.Repository(repo_path)
        workdir = repo.workdir
        rel_path = os.path.relpath(file_path, workdir)

        # Pygit2 blame is highly optimized and runs once per file
        blame = repo.blame(rel_path)

        for line in set(lines):
            # pygit2 uses 1-based indexing for lines
            if line > 0 and line <= len(blame):
                hunk = blame.for_line(line)
                signature = hunk.final_committer
                author = signature.name
                author_email = signature.email
                commit_time = datetime.fromtimestamp(signature.time, tz=timezone.utc).isoformat()

                blame_info[line] = {
                    'author': author,
                    'author_email': author_email,
                    'commit_date': commit_time
                }
    except Exception as e:
        # Silently fail if file is untracked or pygit2 errors out
        logger.debug(f"Failed to get git blame info for {file_path}: {e}")

    return blame_info


def scan_file_worker(
    file_path: str, language: str, config: Optional[Dict], rules: List[Dict]
) -> Dict[str, Any]:
    global _disk_cache_instance
    if config is None:
        config = {}

    try:
        analyzer = EmissionAnalyzer()
        remediation_engine = RemediationEngine()

        cache_config = config.get('cache', {})
        cache_enabled = cache_config.get('enabled', True)
        cache_path = cache_config.get('path', '.green-ai/cache')

        disk_cache = None
        if cache_enabled:
            expanded_path = os.path.expanduser(cache_path)
            if _disk_cache_instance is None or _disk_cache_instance.cache_dir != expanded_path:
                _disk_cache_instance = DiskCache(cache_dir=cache_path)
            disk_cache = _disk_cache_instance

        # Load suppressions fresh per file to avoid global state issues in tests
        external_suppressions = load_external_suppressions()

        issues = []
        emissions = 0.0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            inline_suppressions = get_suppressions(content)

            if language == 'python':
                try:
                    ast.parse(content)
                except SyntaxError:
                    raise

            violations = None
            if disk_cache:
                violations = disk_cache.get(content, language)

            if violations is None:
                violations = detect_violations(content, file_path, language=language)
                if disk_cache:
                    disk_cache.set(content, language, violations)

            violation_lines = [v.get('line', 0) for v in violations if v.get('line')]
            blame_cache = _get_git_blame_info(file_path, violation_lines)

            for violation in violations:
                rule = next((r for r in rules if r['id'] == violation['id']), None)
                if rule:
                    rule_id = rule.get('id', violation.get('id', 'unknown'))
                    rules_config = config.get('rules', {})
                    enabled_rules = rules_config.get('enabled', [])
                    disabled_rules = rules_config.get('disabled', [])
                    severity_overrides = rules_config.get('severity', {})

                    is_enabled = True
                    if rule_id in disabled_rules:
                        is_enabled = False
                    elif rule_id in enabled_rules:
                        is_enabled = True

                    if is_enabled:
                        # Apply severity override if present
                        issue_severity = severity_overrides.get(rule_id, rule.get('severity', 'medium'))

                        v_line = violation.get('line', 0)
                        blame = blame_cache.get(v_line, {})

                        issue = {
                            'id': rule_id,
                            'type': 'green_violation',
                            'severity': issue_severity,
                            'message': violation.get('message', 'N/A'),
                            'file': file_path,
                            'line': v_line,
                            'remediation': rule.get('remediation', 'N/A'),
                            'ai_suggestion': remediation_engine.get_suggestion(rule_id),
                            'effort': rule.get('effort', 'Medium'),
                            'tags': rule.get('tags', []),
                            'carbon_impact': rule.get('carbon_impact', 1e-9),
                            'energy_factor': rule.get('energy_factor', 1),
                            'name': rule.get('name', rule_id),
                            'author': blame.get('author'),
                            'author_email': blame.get('author_email'),
                            'commit_date': blame.get('commit_date')
                        }

                        if not is_suppressed(issue, inline_suppressions, external_suppressions):
                            issues.append(issue)

            if _checks_include(config, 'ai'):
                ai_violations = scan_file_for_ai_usage(file_path)
                for av in ai_violations:
                    rule_id = av['rule_id']
                    issue = {
                        'id': rule_id,
                        'type': 'ai_sustainability',
                        'severity': av['severity'],
                        'message': av['message'],
                        'file': av['file'],
                        'line': av['line'],
                        'remediation': av.get('co2_note', ''),
                        'ai_suggestion': None,
                        'effort': 'Medium',
                        'tags': ['ai', 'sustainability', av.get('provider', 'ai')],
                        'carbon_impact': av.get('estimated_co2_g', 0) * 1e-6,
                        'energy_factor': 1,
                        'name': rule_id.replace('_', ' ').title(),
                        'category': 'ai_sustainability',
                        'co2_note': av.get('co2_note', ''),
                        'provider': av.get('provider'),
                        'model_tier': av.get('model_tier', 'unknown'),
                        'estimated_co2_g': av.get('estimated_co2_g', 0),
                    }
                    if not is_suppressed(issue, inline_suppressions, external_suppressions):
                        issues.append(issue)

            metrics = analyzer.analyze_file(file_path, content)
            emissions = analyzer.estimate_emissions(metrics)

        except SyntaxError:
            issues.append({
                'id': 'syntax_error',
                'type': 'error',
                'severity': 'blocker',
                'message': f'Syntax error in {language} code',
                'file': file_path,
                'line': 0,
                'remediation': 'Fix the syntax error to proceed with scanning.',
                'effort': 'Low',
                'tags': ['syntax', 'error']
            })
        except Exception as e:
            issues.append({
                'id': 'parse_error',
                'type': 'error',
                'severity': 'medium',
                'message': f'Failed to scan file: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Check file content and format.',
                'effort': 'Low',
                'tags': ['error']
            })

        return {
            'issues': issues,
            'emissions': emissions
        }
    except Exception as e:
        return {
            'issues': [{
                'id': 'worker_crash',
                'type': 'error',
                'severity': 'critical',
                'message': f'Worker process crashed: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Report this bug to the maintainers.',
                'effort': 'Low',
                'tags': ['error', 'crash']
            }],
            'emissions': 0.0
        }
