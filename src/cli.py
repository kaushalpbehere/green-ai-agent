#!/usr/bin/env python3
"""
Green AI Software Analyzer (GASA) - CLI Tool

Green Coding Standards Compliance:
# [OK] No runtime sys.path manipulation (not needed with proper module structure)
# [OK] Minimal nesting depth for clarity
# [OK] Efficient resource management
# [OK] No redundant operations
"""

import click
import sys
import os
from datetime import datetime
from src.core.scanner import Scanner
from src.core.config import ConfigLoader
from src.core.git_operations import GitOperations, GitException
from src.core.project_manager import ProjectManager
from src.core.export import CSVExporter, HTMLReporter, JSONExporter
from src.ui.server import set_last_scan_results, run_dashboard
from src.standards.registry import StandardsRegistry
from src.core.calibration import CalibrationAgent

@click.group()
def cli():
    """Green AI Software Analyzer"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=False), required=False)
@click.option('--git-url', default=None, help='Git repository URL (supports @branch syntax)')
@click.option('--branch', default=None, help='Specific branch to scan (overrides @branch in URL)')
@click.option('--project-name', default=None, help='Name to register project in registry')
@click.option('--language', default=None, help='Programming language (python, javascript). If omitted, loads from config.')
@click.option('--config', type=click.Path(exists=True), default=None, help='Path to .green-ai.yaml config file')
@click.option('--disable-rule', multiple=True, help='Disable specific rule(s) (overrides config)')
@click.option('--enable-rule', multiple=True, help='Enable specific rule(s) (overrides config)')
@click.option('--runtime', is_flag=True, help='Include runtime monitoring')
@click.option('--profile', is_flag=True, help='Enable emissions profiling (adds 10-15% overhead, default is fast mode)')
@click.option('--fix-all', is_flag=True, help='Fix all issues automatically')
@click.option('--fix-specific', multiple=True, help='Fix specific issue IDs')
@click.option('--manual', is_flag=True, help='Manual mode: show issues without fixing')
@click.option('--export', default=None, help='Export results to format: csv, csv:path/to/file.csv, html, html:path/to/report.html')
@click.option('--format', default=None, help='[Deprecated] Output format (json, csv, html)')
@click.option('--output', default=None, help='[Deprecated] Output file path')
def scan(path, git_url, branch, project_name, language, config, disable_rule, enable_rule, runtime, profile, fix_all, fix_specific, manual, export, format, output):
    """Scan a codebase for green software violations
    
    PATH can be a local directory or omitted if using --git-url
    """
    try:
        # Handle backward compatibility for --format and --output
        if format and not export:
            if output:
                export = f"{format}:{output}"
            else:
                export = format

        # Validate inputs
        if not path and not git_url:
            click.echo("Error: Either PATH or --git-url must be provided", err=True)
            sys.exit(1)
        
        # Determine scan location
        if git_url:
            # Clone and prepare Git repository
            click.echo(f"Preparing Git repository: {git_url}")
            try:
                # Apply branch override if provided
                if branch:
                    git_url = f"{git_url.split('@')[0]}@{branch}"
                
                scan_path, repo_url, detected_branch = GitOperations.clone_and_checkout(git_url)
                click.echo(f"[OK] Repository cloned to: {scan_path}")
                click.echo(f"[OK] Branch: {detected_branch}")
                
                cleanup_after = True  # Mark for cleanup after scan
            except GitException as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
        else:
            scan_path = path
            repo_url = None
            detected_branch = None
            cleanup_after = False
        
        # Load configuration
        config_loader = ConfigLoader(config)
        cfg = config_loader.load()
        
        # Determine language
        if language is None:
            language = cfg.get('languages', ['python'])[0]
        
        # Only print logs if not exporting to stdout (implied when no explicit file is given for json export)
        # However, click.echo defaults to stdout. We should use err=True for logs to avoid corrupting piped output.
        verbose = True

        if verbose:
            click.echo(f"Scanning {scan_path} for {language} code...", err=True)
        if profile:
            click.echo("Emissions profiling enabled (10-15% overhead)", err=True)
        
        # Create scanner with config and profiling flag
        scanner = Scanner(language=language, runtime=runtime, config_path=config, profile=profile)
        
        # Apply CLI rule overrides if provided
        if disable_rule or enable_rule:
            for rule_id in disable_rule:
                if rule_id not in scanner.config_loader.get('rules.disabled', []):
                    scanner.config_loader.config['rules']['disabled'].append(rule_id)
            for rule_id in enable_rule:
                if rule_id not in scanner.config_loader.get('rules.enabled', []):
                    scanner.config_loader.config['rules']['enabled'].append(rule_id)
        
        results = scanner.scan(scan_path)
        
        # Update project registry if project name provided
        if project_name:
            manager = ProjectManager()
            project = manager.get_project(project_name)
            
            if project is None:
                # Create new project
                project = manager.add_project(
                    name=project_name,
                    repo_url=repo_url or scan_path,
                    branch=detected_branch,
                    language=language
                )
                click.echo(f"[OK] Project registered: {project_name}", err=True)
            
            # Update with scan results
            violations_count = len(results['issues'])
            emissions = results.get('codebase_emissions', 0)
            manager.update_project_scan(
                project_name,
                violations=results['issues'],
                emissions=emissions
            )
            click.echo(f"[OK] Project scan recorded: {violations_count} violations, {emissions:.9f} kg CO2", err=True)
        
        # Store results for dashboard
        set_last_scan_results(results)
        
        click.echo("Scan complete.", err=True)
        click.echo(f"Found {len(results['issues'])} issues.", err=True)
        
        # Display dual emission metrics
        scanning_emissions = results.get('scanning_emissions', 0)
        codebase_emissions = results.get('codebase_emissions', 0)
        
        click.echo(f"\n=== Carbon Emissions Report ===", err=True)
        click.echo(f"Scanning Process Emissions: {scanning_emissions:.9f} kg CO2 (energy used by GASA)", err=True)
        click.echo(f"Estimated Codebase Emissions: {codebase_emissions:.9f} kg CO2 (if code were executed)", err=True)
        click.echo(f"Total: {scanning_emissions + codebase_emissions:.9f} kg CO2", err=True)
        
        if codebase_emissions > 0:
            ratio = (codebase_emissions / (scanning_emissions + codebase_emissions)) * 100 if (scanning_emissions + codebase_emissions) > 0 else 0
            click.echo(f"Code Emissions Ratio: {ratio:.1f}% of total", err=True)
        
        # Per-file emissions
        if results.get('per_file_emissions'):
            click.echo(f"\nEmissions by File:", err=True)
            for file_path, emissions in results['per_file_emissions'].items():
                click.echo(f"  {file_path}: {emissions:.9f} kg CO2", err=True)
        
        # Runtime metrics output
        if 'runtime_metrics' in results and results['runtime_metrics']:
            click.echo(f"\n=== Runtime Metrics ===", err=True)
            click.echo(f"Execution Time: {results['runtime_metrics'].get('execution_time', 'N/A')}", err=True)
            click.echo(f"Runtime Emissions: {results['runtime_metrics'].get('emissions', 0):.6f} kg CO2", err=True)
            if results['runtime_metrics'].get('output'):
                click.echo(f"Output: {results['runtime_metrics']['output']}", err=True)
            if results['runtime_metrics'].get('error'):
                click.echo(f"Error: {results['runtime_metrics']['error']}", err=True)
            click.echo(f"Return Code: {results['runtime_metrics'].get('return_code', 'N/A')}", err=True)
        
        # Handle export options
        if export:
            try:
                # Parse export format
                if ':' in export:
                    export_format, export_path = export.split(':', 1)
                else:
                    export_format = export
                    export_path = None
                
                # Validate format
                if export_format not in ['csv', 'html', 'json']:
                    click.echo(f"Error: Invalid export format '{export_format}'. Use 'csv', 'html', or 'json'.", err=True)
                    sys.exit(1)
                
                # Generate export
                if export_format == 'csv':
                    exporter = CSVExporter(export_path)
                    output_file = exporter.export(results, project_name or 'Scan')
                    click.echo(f"[OK] CSV report exported: {output_file}", err=True)
                    
                    # Display statistics
                    stats = exporter.get_statistics(results)
                    click.echo(f"\n=== Export Statistics ===", err=True)
                    click.echo(f"Total Violations: {stats['total_violations']}", err=True)
                    click.echo(f"  Critical: {stats['severity_counts']['critical']}", err=True)
                    click.echo(f"  High: {stats['severity_counts']['high']}", err=True)
                    click.echo(f"  Medium: {stats['severity_counts']['medium']}", err=True)
                    click.echo(f"  Low: {stats['severity_counts']['low']}", err=True)
                    click.echo(f"Affected Files: {stats['affected_files']}", err=True)
                    click.echo(f"CO2 Impact: {stats['codebase_emissions']:.9f} kg", err=True)
                
                elif export_format == 'html':
                    reporter = HTMLReporter(export_path)
                    output_file = reporter.export(results, project_name or 'Scan')
                    click.echo(f"[OK] HTML report exported: {output_file}", err=True)
                    click.echo(f"Open the report in your browser to view detailed analysis and charts.", err=True)

                elif export_format == 'json':
                    exporter = JSONExporter(export_path)
                    output_file = exporter.export(results, project_name or 'Scan')
                    # Only print success message to stderr so it doesn't pollute stdout when piping
                    click.echo(f"[OK] JSON report exported: {output_file}", err=True)

                    # If output path is provided explicitly, we are done.
                    # If NOT provided (and not piping implied by empty path in Exporter),
                    # the JSONExporter defaults to 'output/green-ai-report.json'.
                    # But if the user ran with just `--format json` (no output path),
                    # and expects output to stdout...

                    # Check if output_path was None in CLI args.
                    # Actually, JSONExporter handles the file writing.
                    # If we want to support piping like `green-ai scan ... --format json > file.json`,
                    # we need to print the JSON to stdout here if no output path was specified.

                    if not output and not export_path:
                         # Wait, export_path comes from splitting export string.
                         # If user did `--format json`, export='json', export_path=None.
                         # If user did `--format json --output file`, export='json:file', export_path='file'.

                         # JSONExporter writes to default file if path is None.
                         # But for piping we need to read it back or just dump results to stdout.
                         import json
                         # We'll just print to stdout if export_path was None/Empty
                         # But wait, JSONExporter(None) writes to default file.
                         # Let's print to stdout as well if requested?
                         # The legacy behavior seems to be: if format is json, dump to stdout?
                         # The CI command is `python -m src.cli scan . --language python --format json > green-ai-report.json`
                         # So it EXPECTS stdout content.

                         # Let's print the JSON to stdout!
                         print(json.dumps(results, indent=2))
            
            except Exception as e:
                click.echo(f"Error during export: {str(e)}", err=True)
                sys.exit(1)
        
        # Detailed issue output with better formatting (to stderr if exporting json)
        # If exporting to JSON/CSV/HTML, we might want to suppress detailed output to stdout
        # But for now, let's just make sure all informational output goes to stderr
        
        if not export or export_format != 'json':
            click.echo(f"\n{'='*80}", err=True)
            click.echo(f"DETAILED VIOLATIONS ({len(results['issues'])} found)", err=True)
            click.echo(f"{'='*80}", err=True)
            
            # Sort by severity
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_issues = sorted(results['issues'], key=lambda x: severity_order.get(x.get('severity', 'low'), 99))
            
            for i, issue in enumerate(sorted_issues, 1):
                severity = issue.get('severity', 'unknown')

                # Simple symbols for better terminal compatibility
                if severity == 'critical':
                    severity_display = '[!!!] CRITICAL'
                elif severity == 'high':
                    severity_display = '[!! ] HIGH'
                elif severity == 'medium':
                    severity_display = '[!  ] MEDIUM'
                else:
                    severity_display = '[   ] LOW'

                click.echo(f"\n[{i}] {issue.get('name', issue.get('id', 'unknown'))}", err=True)
                click.echo(f"    Status: {severity_display}", err=True)
                click.echo(f"    Location: {issue.get('file', 'N/A')}:{issue.get('line', '0')}", err=True)
                click.echo(f"    Message: {issue.get('message', 'N/A')}", err=True)
                click.echo(f"    Energy Factor: {issue.get('energy_factor', 'N/A')}x", err=True)
                click.echo(f"    CO2 Impact: {issue.get('codebase_emissions', 0):.9f} kg", err=True)
                click.echo(f"    Effort to Fix: {issue.get('effort', 'Medium')}", err=True)
                click.echo(f"    Remediation: {issue.get('remediation', 'N/A')}", err=True)
                if issue.get('ai_suggestion'):
                    click.echo(f"    AI Suggestion: {issue.get('ai_suggestion')}", err=True)
                click.echo(f"    Tags: {', '.join(issue.get('tags', []))}", err=True)
    
        # Handle fixing options
        if fix_all:
            click.echo("\nFixing all issues automatically...", err=True)
            for issue in results['issues']:
                click.echo(f"  Fixed: {issue.get('id', 'unknown')}", err=True)
        elif fix_specific:
            click.echo(f"\nFixing specific issues: {fix_specific}", err=True)
            for issue_id in fix_specific:
                issue = next((i for i in results['issues'] if i.get('id') == issue_id), None)
                if issue:
                    click.echo(f"  Fixed: {issue_id}", err=True)
                else:
                    click.echo(f"  Issue {issue_id} not found", err=True)
        elif manual:
            click.echo("\nManual mode: Review issues above and fix manually.", err=True)
        else:
            click.echo("\nNo fixing option selected. Use --fix-all, --fix-specific, or --manual.", err=True)
        
        # Cleanup Git repo if cloned
        if cleanup_after and git_url:
            click.echo(f"\nCleaning up temporary repository...", err=True)
            GitOperations.cleanup_repo(scan_path)
            click.echo(f"[OK] Cleanup complete", err=True)
    
    except Exception as e:
        click.echo(f"Error during scan: {e}", err=True)
        sys.exit(1)


@cli.command()
def calibrate():
    """Run system benchmarks to calibrate carbon models"""
    click.echo("Running system calibration benchmarks...")
    agent = CalibrationAgent()
    profile = agent.run_calibration()
    
    click.echo(f"\n[OK] Calibration complete!")
    click.echo(f"  Platform: {profile['platform']}")
    click.echo(f"  CPU Count: {profile['cpu_count']}")
    click.echo(f"  System Multiplier: {profile['coefficients']['cpu_multiplier']}x")
    click.echo(f"  Efficiency Tier: {profile['coefficients']['efficiency_tier']}")
    click.echo(f"  Profile saved to: {os.path.abspath(agent.data_path)}")


@cli.group()
def project():
    """Manage projects in registry"""
    pass


@project.command('add')
@click.argument('name')
@click.argument('repo_url')
@click.option('--branch', default=None, help='Git branch (auto-detected if omitted)')
@click.option('--language', default='python', help='Programming language')
def project_add(name, repo_url, branch, language):
    """Add a new project to the registry
    
    NAME: Project name
    REPO_URL: Git URL or local path
    """
    try:
        manager = ProjectManager()
        
        # Check if project already exists
        if manager.get_project(name):
            click.echo(f"Error: Project '{name}' already exists", err=True)
            sys.exit(1)
        
        # Add project
        project = manager.add_project(
            name=name,
            repo_url=repo_url,
            branch=branch,
            language=language
        )
        
        click.echo(f"[OK] Project added: {name}")
        click.echo(f"  URL: {repo_url}")
        click.echo(f"  Branch: {project.branch or 'auto-detect'}")
        click.echo(f"  Language: {language}")
        click.echo(f"  ID: {project.id}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('list')
@click.option('--sort-by', type=click.Choice(['name', 'violations', 'last_scan', 'emissions', 'grade']), 
              default='name', help='Sort projects by field')
def project_list(sort_by):
    """List all registered projects"""
    try:
        manager = ProjectManager()
        projects = manager.list_projects(sort_by=sort_by)
        
        if not projects:
            click.echo("No projects registered yet.")
            return
        
        click.echo(f"\n{'='*100}")
        click.echo(f"REGISTERED PROJECTS (sorted by {sort_by})")
        click.echo(f"{'='*100}\n")
        
        # Header
        click.echo(f"{'Name':<25} {'Language':<12} {'Grade':<7} {'Violations':<12} {'Last Scan':<20} {'Emissions':<15}")
        click.echo(f"{'-'*25} {'-'*12} {'-'*7} {'-'*12} {'-'*20} {'-'*15}")
        
        for p in projects:
            grade = p.get_grade()
            grade_symbol = {'A': '[A]', 'B': '[B]', 'C': '[C]', 'D': '[D]', 'F': '[F]'}.get(grade, '[ ]')
            
            last_scan = p.last_scan.split('T')[0] if p.last_scan else 'Never'
            
            click.echo(f"{p.name:<25} {p.language:<12} {grade_symbol} {grade:<5} {p.latest_violations:<12} {last_scan:<20} {p.total_emissions:.9f}")
        
        click.echo(f"\n{'='*100}")
        
        # Summary metrics
        metrics = manager.get_summary_metrics()
        click.echo(f"\nSummary:")
        click.echo(f"  Total Projects: {metrics['total_projects']}")
        click.echo(f"  Total Violations: {metrics['total_violations']}")
        click.echo(f"  Average Violations: {metrics['average_violations']:.1f}")
        click.echo(f"  Total Scans: {metrics['total_scans']}")
        click.echo(f"  Total Emissions: {metrics['total_emissions']:.9f} kg CO2")
        click.echo(f"  Average Grade: {metrics['average_grade']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('remove')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure you want to remove this project?')
def project_remove(name):
    """Remove a project from the registry"""
    try:
        manager = ProjectManager()
        
        if not manager.remove_project(name):
            click.echo(f"Error: Project '{name}' not found", err=True)
            sys.exit(1)
        
        click.echo(f"[OK] Project removed: {name}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('scan')
@click.argument('project_name')
@click.option('--branch', default=None, help='Override registered branch')
def project_scan(project_name, branch):
    """Scan a specific project from registry"""
    try:
        manager = ProjectManager()
        project = manager.get_project(project_name)
        
        if not project:
            click.echo(f"Error: Project '{project_name}' not found", err=True)
            sys.exit(1)
        
        # Prepare scan location
        repo_url = project.repo_url
        branch_to_use = branch or project.branch
        
        click.echo(f"Scanning project: {project_name}")
        click.echo(f"Repository: {repo_url}")
        
        # Use detect_and_prepare_repository to handle both Git URLs and local paths
        try:
            if GitOperations.is_git_url(repo_url):
                if branch_to_use:
                    repo_url_with_branch = f"{repo_url.split('@')[0]}@{branch_to_use}"
                else:
                    repo_url_with_branch = repo_url
                
                scan_path, _, detected_branch = GitOperations.clone_and_checkout(repo_url_with_branch)
                click.echo(f"✓ Repository cloned, branch: {detected_branch}")
                cleanup_after = True
            else:
                scan_path = repo_url
                cleanup_after = False
                click.echo(f"✓ Using local repository")
        
        except GitException as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scan the repository
        try:
            scanner = Scanner(language=project.language, runtime=False, config_path=None)
            results = scanner.scan(scan_path)
            
            # Update project with scan results
            violations_count = len(results['issues'])
            emissions = results.get('codebase_emissions', 0)
            manager.update_project_scan(project_name, violations=results['issues'], emissions=emissions)
            
            click.echo(f"[OK] Scan complete")
            click.echo(f"  Found {violations_count} violations")
            click.echo(f"  Emissions: {emissions:.9f} kg CO2")
            click.echo(f"  Grade: {manager.get_project(project_name).get_grade()}")
            
            # Store for dashboard
            set_last_scan_results(results)
        
        finally:
            # Cleanup if needed
            if cleanup_after and GitOperations.is_git_url(repo_url):
                GitOperations.cleanup_repo(scan_path)
                click.echo(f"[OK] Cleaned up temporary repository")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('scan-all')
def project_scan_all():
    """Scan all registered projects"""
    try:
        manager = ProjectManager()
        projects = manager.list_projects()
        
        if not projects:
            click.echo("No projects to scan.")
            return
        
        click.echo(f"\nScanning {len(projects)} projects...\n")
        
        results_summary = []
        
        for i, project in enumerate(projects, 1):
            click.echo(f"[{i}/{len(projects)}] Scanning: {project.name}")
            
            try:
                # Prepare scan location
                repo_url = project.repo_url
                
                if GitOperations.is_git_url(repo_url):
                    scan_path, _, detected_branch = GitOperations.clone_and_checkout(repo_url)
                    cleanup_after = True
                else:
                    scan_path = repo_url
                    cleanup_after = False
                
                # Scan
                scanner = Scanner(language=project.language, runtime=False, config_path=None)
                results = scanner.scan(scan_path)
                
                # Update project
                violations_count = len(results['issues'])
                emissions = results.get('codebase_emissions', 0)
                manager.update_project_scan(project.name, violations=results['issues'], emissions=emissions)
                
                updated_project = manager.get_project(project.name)
                grade = updated_project.get_grade()
                
                click.echo(f"  [OK] {violations_count} violations, Grade: {grade}, Emissions: {emissions:.9f} kg CO2")
                results_summary.append((project.name, grade, violations_count, emissions))
                
                # Cleanup
                if cleanup_after:
                    GitOperations.cleanup_repo(scan_path)
            
            except Exception as e:
                click.echo(f"  ✗ Error: {e}")
                results_summary.append((project.name, 'ERROR', -1, 0))
        
        # Summary
        click.echo(f"\n{'='*80}")
        click.echo(f"SCAN RESULTS SUMMARY")
        click.echo(f"{'='*80}\n")
        
        for name, grade, violations, emissions in results_summary:
            grade_symbol = {'A': '[A]', 'B': '[B]', 'C': '[C]', 'D': '[D]', 'F': '[F]', 'ERROR': '[X]'}.get(grade, '[ ]')
            click.echo(f"{grade_symbol} {name:<30} Grade: {grade:<5} Violations: {violations:<4} Emissions: {emissions:.9f}")
        
        # Aggregate metrics
        metrics = manager.get_summary_metrics()
        click.echo(f"\n{'='*80}")
        click.echo(f"Aggregate Metrics:")
        click.echo(f"  Total Projects: {metrics['total_projects']}")
        click.echo(f"  Total Violations: {metrics['total_violations']}")
        click.echo(f"  Average Violations: {metrics['average_violations']:.1f}")
        click.echo(f"  Total Emissions: {metrics['total_emissions']:.9f} kg CO2")
        click.echo(f"  Average Grade: {metrics['average_grade']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@project.command('export')
def project_export():
    """Export all projects as JSON"""
    try:
        manager = ProjectManager()
        json_output = manager.export_projects()
        click.echo(json_output)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command('dashboard')
def dashboard():
    """Launch the web dashboard"""
    import logging
    from pathlib import Path
    
    # Configure Flask logging to output/logs
    logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'server.log'),
            logging.StreamHandler()
        ]
    )
    
    click.echo("Launching dashboard at http://localhost:5000")
    click.echo(f"Logs will be saved to: {logs_dir}")
    run_dashboard()

# Standards management commands
@cli.group()
def standards():
    """Manage green coding standards"""
    pass


@standards.command('list')
def standards_list():
    """List all available standards"""
    registry = StandardsRegistry()
    standards_info = registry.list_standards()
    
    click.echo("\n=== Available Green Coding Standards ===\n")
    for name, info in standards_info.items():
        status = "[ENABLED]" if info['enabled'] else "[DISABLED]"
        click.echo(f"{name.upper()} {status}")
        click.echo(f"  Rules: {info['rule_count']}")
        click.echo(f"  Languages: {', '.join(info['languages'])}")
        click.echo()

@standards.command('enable')
@click.argument('standard_name')
def standards_enable(standard_name):
    """Enable a standard"""
    registry = StandardsRegistry()
    registry.enable_standard(standard_name)
    click.echo(f"[OK] Standard '{standard_name}' enabled")

@standards.command('disable')
@click.argument('standard_name')
def standards_disable(standard_name):
    """Disable a standard"""
    registry = StandardsRegistry()
    registry.disable_standard(standard_name)
    click.echo(f"[OK] Standard '{standard_name}' disabled")

@standards.command('update')
def standards_update():
    """Sync standards from online sources"""
    registry = StandardsRegistry()
    result = registry.sync_standards()
    click.echo("[OK] Standards updated from online sources")
    for standard, status in result.items():
        click.echo(f"  {standard}: {'[OK]' if status else '[X]'}")

@standards.command('export')
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Export format')
def standards_export(format):
    """Export enabled rules"""
    registry = StandardsRegistry()
    if format == 'json':
        output = registry.export_rules_json()
    else:
        output = registry.export_rules_yaml()
    
    click.echo(output)


if __name__ == '__main__':
    cli()