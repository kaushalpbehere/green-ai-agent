"""
Scanner module for GASA - Green Software Analyzer

Scans Python and JavaScript codebases for green software violations.
Detects energy inefficiencies and estimates carbon impact.
"""

import os
import ast
import sys
from typing import Optional, Dict, Any, List
from src.core.rules import RuleRepository
from src.core.fixer import AISuggester
from src.core.analyzer import EmissionAnalyzer
from src.core.detectors import detect_violations
from src.core.config import ConfigLoader
from src.core.tracking import create_tracker
from src.core.calibration import CalibrationAgent
from src.core.domain import ScanResult, Violation, ScanMetadata, RuntimeMetrics
from src.utils.logger import logger
import concurrent.futures
import multiprocessing
from multiprocessing import cpu_count

def scan_file_worker(file_path: str, language: str, config: Dict, rules: List[Dict]) -> Dict[str, Any]:
    """
    Worker function to scan and analyze a single file.
    Running in a separate process.
    """
    # Initialize analyzer
    analyzer = EmissionAnalyzer()
    ai_suggester = AISuggester()

    issues = []
    emissions = 0.0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Explicitly check for syntax errors
        if language == 'python':
            ast.parse(content)

        # Scan for violations
        violations = detect_violations(content, file_path, language=language)

        # Convert violations to full issue format
        for violation in violations:
            # Find rule in provided rules list
            rule = next((r for r in rules if r['id'] == violation['id']), None)

            if rule:
                rule_id = rule.get('id', violation.get('id', 'unknown'))

                # Check if rule is enabled in config
                # Re-implement is_rule_enabled logic here since we don't have ConfigLoader instance
                enabled_rules = config.get('rules', {}).get('enabled', [])
                disabled_rules = config.get('rules', {}).get('disabled', [])

                is_enabled = True
                if rule_id in disabled_rules:
                    is_enabled = False
                elif rule_id in enabled_rules:
                    is_enabled = True

                if is_enabled:
                    issue = {
                        'id': rule_id,
                        'type': 'green_violation',
                        'severity': rule.get('severity', 'medium'),
                        'message': violation.get('message', 'N/A'),
                        'file': file_path,
                        'line': violation.get('line', 0),
                        'remediation': rule.get('remediation', 'N/A'),
                        'ai_suggestion': ai_suggester.suggest_fix({'id': rule_id}),
                        'effort': rule.get('effort', 'Medium'),
                        'tags': rule.get('tags', []),
                        'carbon_impact': rule.get('carbon_impact', 0.000000001),
                        'energy_factor': rule.get('energy_factor', 1),
                        'name': rule.get('name', rule_id)
                    }
                    issues.append(issue)

        # Handle parse errors captured by detect_violations (if any custom handling needed)
        # But detect_violations returns dicts, some might be errors?
        # detect_violations returns violations list. Errors are usually raised.

        # Analyze emissions
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
    
    def scan(self, path, progress_callback=None) -> ScanResult:
        """
        Scan a directory or file.
        
        Args:
            path: Path to scan.
            progress_callback: Optional function(message, percentage) for progress reporting.
            
        Returns:
            ScanResult object with scan results.
        """
        # Create appropriate tracker (NoOpTracker by default, ProfilingTracker if --profile)
        tracker = create_tracker(enable_profiling=self.profile)
        tracker.start()
        
        logger.info(f"Starting scan on {path}...")
        
        files = [path] if os.path.isfile(path) else self._get_files(path)
        total_files = len(files)
        
        if total_files == 0:
            tracker.stop()
            return ScanResult(
                issues=[],
                scanning_emissions=0.0,
                codebase_emissions=0.0,
                per_file_emissions={},
                metadata=ScanMetadata(
                    total_files=0,
                    language=self.language,
                    path=str(path)
                )
            )
        
        issues = []
        per_file_emissions = {}
        total_codebase_emissions = 0.0
        
        # Determine number of workers
        num_workers = min(32, (cpu_count() or 1) + 4)
        
        if progress_callback:
            progress_callback("Scanning files...", 10)
            
        processed_count = 0

        # Get rules for the language
        language_rules = self.rule_repo.get_rules(self.language)

        # Use ProcessPoolExecutor for CPU-bound tasks
        # Use 'spawn' context to avoid issues with eventlet monkey patching (fork vs threads)
        mp_context = multiprocessing.get_context('spawn')
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers, mp_context=mp_context) as executor:
            future_to_file = {
                executor.submit(
                    scan_file_worker,
                    f,
                    self.language,
                    self.config,
                    language_rules
                ): f for f in files if self._is_supported_file(f)
            }
            
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
        runtime_metrics_dict = {}
        if self.runtime and self.language == 'python':
            runtime_metrics_dict = self._run_with_monitoring(path)
        
        tracking_result = tracker.stop()
        # Extract emissions value for backward compatibility
        scanning_emissions = tracking_result.get('emissions', 0.0) if isinstance(tracking_result, dict) else tracking_result
        
        # Convert issues to Violation objects
        violation_objects = []
        for issue_data in issues:
            try:
                # Ensure compatibility with Violation model
                if 'energy_factor' in issue_data:
                    # Fix energy_factor if it's "100x" string instead of float, though model allows Union[float, str]
                    pass

                v = Violation(**issue_data)
                violation_objects.append(v)
            except Exception as e:
                logger.error(f"Failed to create Violation object for issue {issue_data.get('id', 'unknown')}: {e}")

        # Create RuntimeMetrics object
        runtime_metrics = None
        if runtime_metrics_dict:
            try:
                runtime_metrics = RuntimeMetrics(**runtime_metrics_dict)
            except Exception as e:
                logger.warning(f"Failed to create RuntimeMetrics: {e}")

        # Construct ScanResult
        results = ScanResult(
            issues=violation_objects,
            scanning_emissions=scanning_emissions,
            scanning_emissions_detailed=tracking_result if isinstance(tracking_result, dict) else {},
            codebase_emissions=total_codebase_emissions,
            per_file_emissions=per_file_emissions,
            runtime_metrics=runtime_metrics,
            metadata=ScanMetadata(
                total_files=total_files,
                language=self.language,
                path=str(path)
            )
        )
        
        if progress_callback:
            progress_callback("Scan complete", 100)
            
        return results
    
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
            
            # Handle dictionary return from tracker
            emissions_val = runtime_emissions.get('emissions', 0.0) if isinstance(runtime_emissions, dict) else runtime_emissions

            return {
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'return_code': result.returncode,
                'execution_time': f"{execution_time:.2f}s",
                'emissions': emissions_val
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
