import os
import sys
import concurrent.futures
import multiprocessing
from typing import Optional, List, Union

from src.core.rules import RuleRepository
from src.core.remediation.engine import RemediationEngine
from src.core.analyzer import EmissionAnalyzer
from src.core.config import ConfigLoader
from src.core.tracking import create_tracker
from src.utils.logger import logger
import click

from src.core.scanner.worker import scan_file_worker
from src.core.scanner.discovery import FileDiscoverer
from src.core.scanner.baseline_helper import load_baseline, filter_with_baseline


class Scanner:
    def __init__(
        self,
        language: str = 'python',
        runtime: bool = False,
        config_path: Optional[str] = None,
        profile: bool = False
    ):
        self.language = language
        self.runtime = runtime
        self.profile = profile
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()
        self.rule_repo = RuleRepository()
        self.emission_analyzer = EmissionAnalyzer()
        self.file_discoverer = FileDiscoverer(
            config_loader=self.config_loader
        )
        self.remediation_engine = RemediationEngine()

    def scan(self, path: Union[str, List[str]], progress_callback=None) -> dict:
        """
        Run a full scan on the given path.

        Args:
            path: Path to scan (file or directory) or list of paths
            progress_callback: Optional function(message, percentage) for progress

        Returns:
            Dictionary of scan results
        """
        tracker = create_tracker(enable_profiling=self.profile)
        tracker.start()

        logger.info(f"Starting scan on {path}...")

        scan_metadata_path = ""

        if isinstance(path, str):
            files_gen = self.file_discoverer.get_files(path)
            scan_metadata_path = path
        else:
            def chained_gen():
                for p in path:
                    yield from self.file_discoverer.get_files(p)
            files_gen = chained_gen()
            scan_metadata_path = f"Multiple paths ({len(path)})"

        files_to_scan = [f for f in files_gen if self._is_supported_file(f)]
        total_files = len(files_to_scan)

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

        config_concurrency = self.config.get('concurrency')
        if config_concurrency:
            num_workers = int(config_concurrency)
        else:
            cpus = os.cpu_count() or 1
            num_workers = max(1, min(32, cpus - 1)) if cpus > 1 else 1

        if progress_callback:
            progress_callback("Scanning files...", 10)

        processed_count = 0
        language_rules = self.rule_repo.get_rules(self.language)

        mp_context = multiprocessing.get_context('spawn')

        if total_files > 0:
            kwargs = {}
            if sys.version_info >= (3, 11):
                kwargs['max_tasks_per_child'] = 50

            with concurrent.futures.ProcessPoolExecutor(
                max_workers=num_workers, mp_context=mp_context, **kwargs
            ) as executor:
                # Use executor.submit and as_completed for accurate progress state sync
                futures = {
                    executor.submit(
                        scan_file_worker,
                        file_path,
                        self.language,
                        self.config,
                        language_rules
                    ): file_path for file_path in files_to_scan
                }

                for future in concurrent.futures.as_completed(futures):
                    file_path = futures[future]
                    try:
                        file_result = future.result()
                        issues.extend(file_result['issues'])
                        per_file_emissions[file_path] = file_result['emissions']
                        total_codebase_emissions += file_result['emissions']

                        processed_count += 1
                        if progress_callback and total_files > 0:
                            percentage = 10 + int(
                                (processed_count / total_files) * 80
                            )
                            progress_callback(
                                f"Processing {os.path.basename(file_path)}",
                                percentage
                            )
                    except Exception as exc:
                        logger.error(f"{file_path} generated an exception: {exc}")

        if progress_callback:
            progress_callback("Finalizing scan results...", 95)

        # Apply baseline filtering (BASE-002)
        baseline = load_baseline()
        issues, skipped_count, fixed_count = filter_with_baseline(issues, baseline)

        # Distribute codebase emissions across issues
        issues = self.emission_analyzer.get_per_line_emissions(
            issues, total_codebase_emissions
        )

        runtime_metrics = {}
        if self.runtime and self.language == 'python':
            runtime_metrics = self._run_with_monitoring(path)

        tracking_result = tracker.stop()
        scanning_emissions = tracking_result.get('emissions', 0.0) \
            if isinstance(tracking_result, dict) else tracking_result

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
                'path': scan_metadata_path,
                'baseline_skipped': skipped_count,
                'baseline_fixed': fixed_count
            }
        }

        if skipped_count > 0 or fixed_count > 0:
            click.echo(f"Baseline Delta: {len(issues)} new, {skipped_count} ignored, {fixed_count} fixed.")

        if progress_callback:
            progress_callback("Scan complete", 100)

        return results

    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file extension matches current language."""
        ext_map = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'c-sharp': ['.cs'],
            'rust': ['.rs']
        }
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ext_map.get(self.language, [])

    def _run_with_monitoring(self, path):
        if isinstance(path, list):
            return {
                'error': 'Runtime monitoring requires a single entry point path'
            }

        if not os.path.isfile(path):
            return {'error': 'Runtime monitoring requires a single file path'}

        command = self._get_run_command(path)
        if not command:
            return {
                'error': f'Could not determine run command for {self.language}'
            }

        from src.agents.runtime_monitor.main import RuntimeMonitor
        monitor = RuntimeMonitor()
        return monitor.monitor_execution(command)

    def _get_run_command(self, path: str) -> Optional[List[str]]:
        """Determine command to run the script."""
        if self.language == 'python':
            return [sys.executable, path]
        if self.language == "javascript":
            return ["node", path]
        return None
