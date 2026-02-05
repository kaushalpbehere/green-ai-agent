"""
Scanner module for GASA - Green Software Analyzer

Scans Python and JavaScript codebases for green software violations.
Detects energy inefficiencies and estimates carbon impact.
"""

import os
import ast
import sys
from typing import Optional, Dict, Any
from src.core.rules import RuleRepository
from src.core.fixer import AISuggester
from src.core.analyzer import EmissionAnalyzer
from src.core.detectors import detect_violations
from src.core.config import ConfigLoader
from src.core.tracking import create_tracker
from src.core.calibration import CalibrationAgent
from src.utils.logger import logger
import concurrent.futures
from multiprocessing import cpu_count

class Scanner:
    def __init__(self, language: Optional[str] = None, runtime: bool = False, config_path: Optional[str] = None, profile: bool = False):
        """
        Initialize scanner.
        
        Args:
            language: Language to scan (python, javascript). If None, loaded from config.
            runtime: Enable runtime monitoring (not yet implemented).
            config_path: Path to .green-ai.yaml config file. If None, auto-discovers.
            profile: Enable emissions profiling. If False (default), uses NoOpTracker for 0% overhead.
        """
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()
        
        # Use provided language or load from config
        self.language = language or self.config_loader.get_enabled_languages()[0]
        self.runtime = runtime
        self.profile = profile
        self.parser = self._setup_parser()
        self.rule_repo = RuleRepository()
        self.ai_suggester = AISuggester()
        
        # Load system calibration
        self.calibration_agent = CalibrationAgent()
        self.emission_analyzer = EmissionAnalyzer(
            calibration_coefficient=self.calibration_agent.get_coefficient()
        )
        
    def _setup_parser(self):
        # For now, use Python ast for both
        return None
    
    def scan(self, path, progress_callback=None):
        """
        Scan a directory or file.
        
        Args:
            path: Path to scan.
            progress_callback: Optional function(message, percentage) for progress reporting.
            
        Returns:
            Dictionary with scan results.
        """
        # Create appropriate tracker (NoOpTracker by default, ProfilingTracker if --profile)
        tracker = create_tracker(enable_profiling=self.profile)
        tracker.start()
        
        logger.info(f"Starting scan on {path}...")
        
        files = [path] if os.path.isfile(path) else self._get_files(path)
        total_files = len(files)
        
        if total_files == 0:
            tracker.stop()
            return {
                'issues': [],
                'scanning_emissions': 0,
                'codebase_emissions': 0,
                'per_file_emissions': {},
                'metadata': {'total_files': 0}
            }
        
        issues = []
        per_file_emissions = {}
        total_codebase_emissions = 0.0
        
        # Determine number of workers
        num_workers = min(32, (cpu_count() or 1) + 4)
        
        if progress_callback:
            progress_callback("Scanning files...", 10)
            
        processed_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_file = {executor.submit(self._scan_and_analyze_file, f): f for f in files if self._is_supported_file(f)}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    issues.extend(file_result['issues'])
                    per_file_emissions[file_path] = file_result['emissions']
                    total_codebase_emissions += file_result['emissions']
                    
                    processed_count += 1
                    if progress_callback and total_files > 0:
                        percentage = 10 + int((processed_count / total_files) * 80)
                        progress_callback(f"Processing {os.path.basename(file_path)}", percentage)
                except Exception as exc:
                    logger.error(f"{file_path} generated an exception: {exc}")
        
        if progress_callback:
            progress_callback("Finalizing scan results...", 95)
            
        # Distribute codebase emissions across issues
        issues = self.emission_analyzer.get_per_line_emissions(issues, total_codebase_emissions)
        
        # Runtime monitoring if enabled
        runtime_metrics = {}
        if self.runtime and self.language == 'python':
            runtime_metrics = self._run_with_monitoring(path)
        
        tracking_result = tracker.stop()
        # Extract emissions value for backward compatibility
        scanning_emissions = tracking_result.get('emissions', 0.0) if isinstance(tracking_result, dict) else tracking_result
        
        results = {
            'issues': issues,
            'scanning_emissions': scanning_emissions,
            'scanning_emissions_detailed': tracking_result,
            'codebase_emissions': total_codebase_emissions,
            'per_file_emissions': per_file_emissions,
            'runtime_metrics': runtime_metrics,
            'metadata': {
                'total_files': total_files,
                'language': self.language,
                'path': path
            }
        }
        
        if progress_callback:
            progress_callback("Scan complete", 100)
            
        return results

    def _scan_and_analyze_file(self, file_path: str) -> Dict[str, Any]:
        """ Helper method for worker processes to scan and analyze a single file. """
        # Re-initialize analyzer for each worker process (if needed, or pass it in)
        # Note: EmissionAnalyzer must be process-safe or re-instantiated
        from src.core.analyzer import EmissionAnalyzer
        analyzer = EmissionAnalyzer()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Scan for violations
            file_issues = self._scan_file(file_path, content)
            
            # Analyze emissions
            metrics = analyzer.analyze_file(file_path, content)
            emissions = analyzer.estimate_emissions(metrics)
            
            return {
                'issues': file_issues,
                'emissions': emissions
            }
        except Exception as e:
            raise e
    
    def _run_with_monitoring(self, path):
        """Safely execute code and monitor basic runtime metrics."""
        if not os.path.isfile(path):
            return {'error': 'Runtime monitoring requires a single file path'}
        
        command = self._get_run_command(path)
        if not command:
            return {'error': f'Runtime monitoring not supported for language {self.language}'}
        
        try:
            import subprocess
            import time
            
            # Use profiling tracker for runtime monitoring
            runtime_tracker = create_tracker(enable_profiling=True)
            runtime_tracker.start()
            
            start_time = time.time()
            
            # Execute the script with timeout
            result = subprocess.run(command, 
                                  capture_output=True, text=True, timeout=30)
            
            execution_time = time.time() - start_time
            runtime_emissions = runtime_tracker.stop()
            
            return {
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'return_code': result.returncode,
                'execution_time': f"{execution_time:.2f}s",
                'emissions': runtime_emissions
            }
                
        except subprocess.TimeoutExpired:
            runtime_tracker.stop()  # Stop tracker even on timeout
            return {
                'error': 'Execution timed out after 30 seconds',
                'execution_time': '>30s',
                'emissions': 0.0
            }
        except Exception as e:
            try:
                runtime_tracker.stop()
            except:
                pass
            return {
                'error': str(e),
                'execution_time': 'N/A',
                'emissions': 0.0
            }
    
    def _get_files(self, scan_path):
        """
        Get all files to scan, respecting ignore patterns from config.
        
        Uses pathlib for efficiency and correct cross-platform path handling.
        """
        from pathlib import Path
        import fnmatch
        
        path = Path(scan_path)
        if path.is_file():
            return [str(path)]
            
        ignore_patterns = self.config_loader.get_ignored_files()
        all_files = []
        
        logger.info(f"Discovering files in {scan_path} (Ignoring: {', '.join(ignore_patterns)})")
        
        # Walk using path.glob or rglob while filtering
        for file in path.rglob('*'):
            if not file.is_file():
                continue
                
            # Check relative path against ignore patterns
            rel_path = file.relative_to(path)
            rel_str = str(rel_path).replace('\\', '/') # Standardize for matching
            
            is_ignored = False
            for pattern in ignore_patterns:
                # Match against filename and path parts
                if fnmatch.fnmatch(rel_str, pattern) or any(fnmatch.fnmatch(part, pattern) for part in rel_path.parts):
                    is_ignored = True
                    break
            
            if not is_ignored:
                all_files.append(str(file))
                
        logger.info(f"Found {len(all_files)} files to scan.")
        return all_files
    
    def _get_run_command(self, path):
        if self.language == 'python':
            return [sys.executable, path]
        elif self.language == 'javascript':
            return ['node', path]
        else:
            return None
    
    def _is_supported_file(self, file_path):
        if self.language == 'python':
            return file_path.endswith('.py')
        elif self.language == 'javascript':
            return file_path.endswith('.js')
        return False
    
    def _scan_file(self, file_path, content=None):
        issues = []
        try:
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if self.language == 'python':
                issues.extend(self._scan_python(content, file_path))
            elif self.language == 'javascript':
                issues.extend(self._scan_javascript(content, file_path))
                
        except Exception as e:
            issues.append({
                'id': 'scan_error',
                'type': 'error',
                'message': f"Failed to scan file: {str(e)}",
                'file': file_path,
                'line': 0,
                'severity': 'low',
                'remediation': 'Check file format and encoding.',
                'effort': 'Low',
                'tags': ['error']
            })
        
        # Filter issues based on configuration
        issues = self._filter_issues_by_config(issues)
        return issues
    
    def _filter_issues_by_config(self, issues: list) -> list:
        """
        Filter issues based on configuration (enabled/disabled rules).
        
        Args:
            issues: List of detected issues
            
        Returns:
            Filtered list of issues
        """
        filtered = []
        for issue in issues:
            rule_id = issue.get('id')
            
            # Keep non-violation issues (errors, etc.)
            if issue.get('type') != 'green_violation':
                filtered.append(issue)
                continue
            
            # Check if rule is enabled in config
            if self.config_loader.is_rule_enabled(rule_id):
                filtered.append(issue)
        
        return filtered
    
    def _scan_python(self, content, file_path):
        """Scan Python file for green software violations."""
        issues = []
        
        try:
            # Use enhanced detection system
            violations = detect_violations(content, file_path, language='python')
            
            # Get rules repository for detailed information
            rule_repo = self.rule_repo
            
            # Convert violations to full issue format
            for violation in violations:
                rule = rule_repo.get_rule('python', violation['id'])
                
                if rule:
                    rule_id = rule.get('id', violation.get('id', 'unknown'))
                    issue = {
                        'id': rule_id,
                        'type': 'green_violation',
                        'severity': rule.get('severity', 'medium'),
                        'message': violation.get('message', 'N/A'),
                        'file': file_path,
                        'line': violation.get('line', 0),
                        'remediation': rule.get('remediation', 'N/A'),
                        'ai_suggestion': self.ai_suggester.suggest_fix({'id': rule_id}),
                        'effort': rule.get('effort', 'Medium'),
                        'tags': rule.get('tags', []),
                        'carbon_impact': rule.get('carbon_impact', 0.000000001),
                        'energy_factor': rule.get('energy_factor', 1),
                        'name': rule.get('name', rule_id)
                    }
                    issues.append(issue)
            
        except SyntaxError:
            issues.append({
                'id': 'syntax_error',
                'type': 'error',
                'severity': 'blocker',
                'message': 'Syntax error in Python code',
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
                'message': f'Failed to parse Python file: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Check file content and format.',
                'effort': 'Low',
                'tags': ['error']
            })
        
        return issues
    
    def _scan_javascript(self, content, file_path):
        """Scan JavaScript file for green software violations."""
        issues = []
        
        try:
            violations = detect_violations(content, file_path, language='javascript')
            rule_repo = self.rule_repo
            
            for violation in violations:
                rule = rule_repo.get_rule('javascript', violation['id'])
                
                if rule:
                    rule_id = rule.get('id', violation.get('id', 'unknown'))
                    issue = {
                        'id': rule_id,
                        'type': 'green_violation',
                        'severity': rule.get('severity', 'medium'),
                        'message': violation.get('message', 'N/A'),
                        'file': file_path,
                        'line': violation.get('line', 0),
                        'remediation': rule.get('remediation', 'N/A'),
                        'ai_suggestion': self.ai_suggester.suggest_fix({'id': rule_id}),
                        'effort': rule.get('effort', 'Medium'),
                        'tags': rule.get('tags', []),
                        'carbon_impact': rule.get('carbon_impact', 0.000000001),
                        'energy_factor': rule.get('energy_factor', 1),
                        'name': rule.get('name', rule_id)
                    }
                    issues.append(issue)
        
        except Exception as e:
            issues.append({
                'id': 'parse_error',
                'type': 'error',
                'severity': 'medium',
                'message': f'Failed to parse JavaScript file: {str(e)}',
                'file': file_path,
                'line': 0,
                'remediation': 'Check file content and format.',
                'effort': 'Low',
                'tags': ['error']
            })