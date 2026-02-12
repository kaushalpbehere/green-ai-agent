"""
Dashboard module for Green AI Agent
"""

import eventlet
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import json
import sys
import os
from typing import Any

from src.standards.registry import StandardsRegistry
from src.ui.charts import generate_all_charts
from src.core.project_manager import ProjectManager
from src.core.history import HistoryManager
from src.core.scanner import Scanner
from src.core.remediation import RemediationAgent
from src.utils.metrics import calculate_projects_grade, calculate_average_grade
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store last scan results
last_scan_results = None
last_charts = None
standards_registry = None
project_manager = None
history_manager = None
remediation_agent = None

def get_standards_registry():
    global standards_registry
    if standards_registry is None:
        standards_registry = StandardsRegistry()
    return standards_registry

def get_project_manager():
    global project_manager
    if project_manager is None:
        project_manager = ProjectManager()
    return project_manager

def get_history_manager():
    global history_manager
    if history_manager is None:
        history_manager = HistoryManager()
    return history_manager

def get_remediation_agent():
    global remediation_agent
    if remediation_agent is None:
        remediation_agent = RemediationAgent()
    return remediation_agent


def broadcast_progress(message, percentage):
    """Broadcast scan progress to all connected clients."""
    socketio.emit('scan_progress', {'message': message, 'percentage': percentage})

def initialize_app():
    """Initialize default project and trigger scan if needed."""
    # Ensure globals are initialized
    pm = get_project_manager()
    hm = get_history_manager()
    get_standards_registry()
    get_remediation_agent()

    try:
        default_project = pm.get_project("Green-AI Agent")
        # Force use the local path for the default project
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if not default_project:
            pm.add_project(
                name="Green-AI Agent",
                repo_url=root_dir,
                branch="main",
                language="python",
                is_system=True
            )
            print(f"Initialized default project at {root_dir}", file=sys.stderr)

        # Trigger initial scan in background if last_scan is None
        default_project = pm.get_project("Green-AI Agent")
        if default_project and not default_project.last_scan:
            print("Triggering initial background scan for Green-AI Agent...", file=sys.stderr)
            def initial_scan():
                try:
                    scanner = Scanner(language="python")
                    results = scanner.scan(root_dir)
                    set_last_scan_results(results)
                    hm.add_scan("Green-AI Agent", results)
                    pm.update_project_scan("Green-AI Agent", results['issues'], results.get('total_emissions', 0))
                    print("Initial scan completed.", file=sys.stderr)
                except Exception as e:
                    print(f"Initial scan failed: {e}", file=sys.stderr)

            scan_thread = threading.Thread(target=initial_scan)
            scan_thread.daemon = True
            scan_thread.start()
    except Exception as e:
        print(f"Warning: Could not initialize default project: {e}", file=sys.stderr)

def set_last_scan_results(results):
    global last_scan_results, last_charts
    last_scan_results = results
    last_charts = generate_all_charts(results)

@app.route('/')
def dashboard():
    if last_scan_results:
        insights = generate_insights(last_scan_results)
        return render_template_string(get_dashboard_html(), results=last_scan_results, insights=insights, charts=last_charts)
    else:
        # Show enhanced landing page with stats
        projects = get_project_manager().list_projects()
        total_violations = sum(p.latest_violations for p in projects)
        avg_grade = calculate_projects_grade(projects) if projects else "N/A"
        recent_projects = sorted(projects, key=lambda p: p.last_scan or "", reverse=True)[:5]

        return render_template_string(get_landing_page_html(),
                                     projects=projects,
                                     total_violations=total_violations,
                                     avg_grade=avg_grade,
                                     recent_projects=recent_projects,
                                     project_count=len(projects))

@app.route('/api/charts')
def api_charts() -> Any:
    """Return all chart data as JSON"""
    return jsonify(last_charts) if last_charts else jsonify({})

@app.route('/api/results')
def api_results() -> Any:
    return jsonify(last_scan_results) if last_scan_results else jsonify({})

# Standards API Endpoints
@app.route('/api/standards')
def api_standards_list() -> Any:
    """List all available standards"""
    return jsonify(get_standards_registry().list_standards())

@app.route('/api/standards/<standard_name>/enable', methods=['POST'])
def api_enable_standard(standard_name) -> Any:
    """Enable a standard"""
    get_standards_registry().enable_standard(standard_name)
    return jsonify({'status': 'ok', 'message': f'Standard {standard_name} enabled'})

@app.route('/api/standards/<standard_name>/disable', methods=['POST'])
def api_disable_standard(standard_name) -> Any:
    """Disable a standard"""
    get_standards_registry().disable_standard(standard_name)
    return jsonify({'status': 'ok', 'message': f'Standard {standard_name} disabled'})

@app.route('/api/standards/<standard_name>/rules')
def api_standard_rules(standard_name) -> Any:
    """Get rules for a specific standard"""
    registry = get_standards_registry()
    if standard_name in registry.standards:
        rules = registry.standards[standard_name]
        return jsonify({
            'standard': standard_name,
            'rule_count': len(rules),
            'rules': [{'id': r.id, 'name': r.name, 'severity': r.severity} for r in rules]
        })
    return jsonify({'error': 'Standard not found'}), 404

@app.route('/api/rules/<rule_id>/disable', methods=['POST'])
def api_disable_rule(rule_id) -> Any:
    """Disable a specific rule"""
    get_standards_registry().disable_rule(rule_id)
    return jsonify({'status': 'ok', 'message': f'Rule {rule_id} disabled'})

@app.route('/api/rules/<rule_id>/enable', methods=['POST'])
def api_enable_rule(rule_id) -> Any:
    """Enable a specific rule"""
    get_standards_registry().enable_rule(rule_id)
    return jsonify({'status': 'ok', 'message': f'Rule {rule_id} enabled'})

@app.route('/api/standards/export/<format>')
def api_export_rules(format) -> Any:
    """Export rules in specified format"""
    if format == 'json':
        return get_standards_registry().export_rules_json()
    elif format == 'yaml':
        return get_standards_registry().export_rules_yaml()
    else:
        return jsonify({'error': 'Invalid format'}), 400


# Projects API Endpoints
@app.route('/api/projects')
def api_projects_list() -> Any:
    """List all projects with their metrics"""
    projects = get_project_manager().list_projects()

    projects_data = []
    for project in projects:
        project_info = {
            'id': project.id,
            'name': project.name,
            'language': project.language,
            'url': project.repo_url,
            'branch': project.branch,
            'last_scan_time': project.last_scan,
            'health_grade': project.get_grade(),
            'violation_count': project.latest_violations,
            'high_violations': project.high_violations,
            'medium_violations': project.medium_violations,
            'low_violations': project.low_violations,
            'scanning_emissions': project.total_emissions, # Using total for now
            'codebase_emissions': 0,
            'total_emissions': project.total_emissions,
            'created_date': None,
            'created_by': 'system',
        }
        projects_data.append(project_info)

    return jsonify({
        'status': 'ok',
        'total_projects': len(projects_data),
        'projects': projects_data,
        'summary': {
            'total_violations': sum(p['violation_count'] for p in projects_data),
            'total_high_violations': sum(p['high_violations'] for p in projects_data),
            'average_grade': calculate_projects_grade(projects),
            'combined_emissions': sum(p['total_emissions'] for p in projects_data),
        }
    })

@app.route('/api/projects/<project_name>')
def api_project_detail(project_name) -> Any:
    """Get detailed view of a single project"""
    project = get_project_manager().get_project(project_name)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    project_dict = project.to_dict()
    project_dict['health_grade'] = project.get_grade()
    # violations are now part of project_dict via to_dict()

    return jsonify({
        'status': 'ok',
        'project': project_dict
    })

@app.route('/api/projects/comparison')
def api_projects_comparison() -> Any:
    """Get comparison data for multiple projects"""
    # Get project names from query params
    project_names = request.args.getlist('projects')

    if not project_names or len(project_names) == 0:
        return jsonify({'error': 'No projects specified. Use ?projects=name1&projects=name2'}), 400

    if len(project_names) > 5:
        return jsonify({'error': 'Maximum 5 projects can be compared at once'}), 400

    comparison_data = []
    pm = get_project_manager()
    for project_name in project_names:
        project = pm.get_project(project_name)
        if project:
            comparison_data.append({
                'name': project.name,
                'language': project.language,
                'health_grade': project.get_grade(),
                'violation_count': project.latest_violations,
                'high_violations': 0,
                'medium_violations': 0,
                'low_violations': 0,
                'scanning_emissions': project.total_emissions,
                'codebase_emissions': 0,
                'total_emissions': project.total_emissions,
                'last_scan_time': project.last_scan,
            })

    if not comparison_data:
        return jsonify({'error': 'No valid projects found'}), 404

    return jsonify({
        'status': 'ok',
        'comparison_count': len(comparison_data),
        'projects': comparison_data
    })


# Scan Management Endpoints
@app.route('/api/scan', methods=['POST'])
def api_scan() -> Any:
    """Execute a new scan on project"""
    data = request.get_json()

    project_name = data.get('project_name')
    language = data.get('language')
    git_url = data.get('git_url')
    path = data.get('path')

    if not project_name or not language:
        return jsonify({'error': 'project_name and language are required'}), 400

    if not git_url and not path:
        return jsonify({'error': 'Either git_url or path is required'}), 400

    pm = get_project_manager()
    # Check if project exists, create if not
    existing = pm.get_project(project_name)
    if not existing:
        pm.add_project(project_name, repo_url=git_url or path, language=language)

    # Start background scan
    def run_background_scan():
        try:
            broadcast_progress("Starting background scan...", 5)
            # Initialize scanner
            # Note: We might need to handle git cloning here if git_url is provided
            # For simplicity, we assume path is local for now or already cloned
            scan_path = path or git_url # Simple hack for now

            # If it's a git URL, we should clone it (but that's complex to re-implement here)
            # For now, let's just use the scanner on the path
            scanner = Scanner(language=language)

            def progress_cb(msg, pct):
                broadcast_progress(msg, pct)

            results = scanner.scan(scan_path, progress_callback=progress_cb)

            # Update results and charts
            set_last_scan_results(results)

            # Record in history
            get_history_manager().add_scan(project_name, results)

            broadcast_progress("Scan complete!", 100)
            socketio.emit('scan_finished', {'project_name': project_name})

        except Exception as e:
            print(f"Background scan error: {e}", file=sys.stderr)
            broadcast_progress(f"Error: {str(e)}", 0)
            socketio.emit('scan_error', {'error': str(e)})

    thread = threading.Thread(target=run_background_scan)
    thread.daemon = True
    thread.start()

    return jsonify({
        'status': 'ok',
        'message': f'Scan initiated for {project_name}',
        'project_name': project_name,
        'scan_type': 'git' if git_url else 'local',
        'language': language
    })


@app.route('/api/projects/<project_name>', methods=['DELETE'])
def api_delete_project(project_name) -> Any:
    """Delete a project"""
    try:
        pm = get_project_manager()
        project = pm.get_project(project_name)
        if not project:
            return jsonify({'error': f'Project {project_name} not found'}), 404

        if project.is_system:
            return jsonify({'error': f'Cannot delete system project: {project_name}'}), 403

        pm.remove_project(project_name)
        return jsonify({
            'status': 'ok',
            'message': f'Project {project_name} deleted'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/projects/<project_name>/rescan', methods=['POST'])
def api_rescan_project(project_name) -> Any:
    """Rescan an existing project"""
    try:
        project = get_project_manager().get_project(project_name)

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        url = project.repo_url
        language = project.language

        return jsonify({
            'status': 'ok',
            'message': f'Rescan initiated for {project_name}',
            'project_name': project_name,
            'url': url,
            'language': language
        })
    except Exception as e:
        return jsonify({'error': f'Failed to rescan project: {str(e)}'}), 500


@app.route('/api/projects/<project_name>/clear', methods=['POST'])
def api_clear_project(project_name) -> Any:
    """Clear violations and rescan project"""
    try:
        pm = get_project_manager()
        project = pm.get_project(project_name)

        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Clear violations
        # Reset fields if needed (Project object doesn't have violations list directly)
        project.latest_violations = 0
        project.total_emissions = 0.0
        pm._save_projects()

        return jsonify({
            'status': 'ok',
            'message': f'Project {project_name} cleared and ready for rescan'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to clear project: {str(e)}'}), 500


@app.route('/api/export/csv', methods=['GET'])
def api_export_csv() -> Any:
    """Export scan results to CSV"""
    try:
        from src.core.export import CSVExporter
        import json
        from io import StringIO

        # Get project name from query params or use last scan
        project_name = request.args.get('project', 'Scan')

        if not last_scan_results:
            return jsonify({'error': 'No scan results available. Run a scan first.'}), 400

        # Create CSV in output directory
        from pathlib import Path
        output_dir = Path(__file__).parent.parent.parent / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_exporter = CSVExporter()
        output_path = output_dir / f'green-ai-report-{project_name}.csv'
        csv_exporter.output_path = str(output_path)
        csv_exporter.export(last_scan_results, project_name)

        # Read and return CSV file
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            csv_content = f.read()

        # Clean up temp file
        import os
        if os.path.exists(output_path):
            os.remove(output_path)

        return csv_content, 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{output_path}"'
        }
    except Exception as e:
        return jsonify({'error': f'Failed to export CSV: {str(e)}'}), 500


@app.route('/api/export/html', methods=['GET'])
def api_export_html() -> Any:
    """Export scan results to HTML report"""
    try:
        from src.core.export import HTMLReporter

        # Get project name from query params
        project_name = request.args.get('project', 'Scan')

        if not last_scan_results:
            return jsonify({'error': 'No scan results available. Run a scan first.'}), 400

        # Create HTML report in output directory
        from pathlib import Path
        output_dir = Path(__file__).parent.parent.parent / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)

        html_reporter = HTMLReporter()
        output_path = output_dir / f'green-ai-report-{project_name}.html'
        html_reporter.output_path = str(output_path)
        html_reporter.export(last_scan_results, project_name)

        # Read and return HTML file
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Clean up temp file
        import os
        if os.path.exists(output_path):
            os.remove(output_path)

        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': f'Failed to export HTML: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def api_get_history() -> Any:
    """Get historical scan data for a project"""
    try:
        project_name = request.args.get('project')
        days = request.args.get('days', type=int, default=None)

        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400

        scans = get_history_manager().get_project_history(project_name, days=days)

        return jsonify({
            'project': project_name,
            'scans': [s.to_dict() for s in scans],
            'count': len(scans)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500


@app.route('/api/trending', methods=['GET'])
def api_get_trending() -> Any:
    """Get trending analysis for a project"""
    try:
        project_name = request.args.get('project')
        days = request.args.get('days', type=int, default=None)

        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400

        trending = get_history_manager().get_trending_data(project_name, days=days)

        return jsonify({
            'project': project_name,
            'trend': trending['trend'],
            'details': trending,
            'grade_improvement': trending.get('grade_improvement', 'N/A')
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get trending: {str(e)}'}), 500


@app.route('/api/compare', methods=['GET'])
def api_compare_scans() -> Any:
    """Compare two scans in project history"""
    try:
        project_name = request.args.get('project')
        scan1_idx = request.args.get('scan1', type=int, default=-2)
        scan2_idx = request.args.get('scan2', type=int, default=-1)

        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400

        hm = get_history_manager()
        scans = hm.get_project_history(project_name)

        if len(scans) < 2:
            return jsonify({'error': 'Not enough scans to compare'}), 400

        scan1 = scans[scan1_idx] if scan1_idx < len(scans) else scans[0]
        scan2 = scans[scan2_idx] if scan2_idx < len(scans) else scans[-1]

        comparison = hm.compare_scans(scan1, scan2)

        return jsonify({
            'project': project_name,
            'scan1_timestamp': scan1.timestamp,
            'scan2_timestamp': scan2.timestamp,
            'new_violations': comparison['changes']['new_violations'],
            'fixed_violations': comparison['changes']['fixed_violations'],
            'grade_change': comparison.get('grade_change', 'N/A'),
            'details': comparison.get('details', {})
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to compare scans: {str(e)}'}), 500


@app.route('/api/remediation/preview', methods=['GET'])
def api_remediation_preview() -> Any:
    """Get a preview of the suggested remediation diff"""
    project_name = request.args.get('project')
    file_path = request.args.get('file')
    line = request.args.get('line', type=int)
    issue_id = request.args.get('issue_id')

    if not all([project_name, file_path, line, issue_id]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Read the original file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        agent = get_remediation_agent()
        diff = agent.get_remediation_diff(file_path, line, issue_id, content)
        description = agent.get_fix_description(issue_id)

        return jsonify({
            'status': 'ok',
            'diff': diff,
            'description': description
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500





def load_template(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), 'templates', name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading template {name}: {e}", file=sys.stderr)
        return f"<h1>Error: Template {name} could not be loaded</h1><p>{str(e)}</p>"

LANDING_PAGE_HTML = None
DASHBOARD_HTML = None

def get_landing_page_html():
    global LANDING_PAGE_HTML
    if LANDING_PAGE_HTML is None:
        LANDING_PAGE_HTML = load_template('landing.html')
    return LANDING_PAGE_HTML

def get_dashboard_html():
    global DASHBOARD_HTML
    if DASHBOARD_HTML is None:
        DASHBOARD_HTML = load_template('dashboard.html')
    return DASHBOARD_HTML

def generate_insights(results):
    insights = []
    issue_count = len(results['issues'])

    if issue_count > 5:
        insights.append("High number of issues detected. Consider refactoring the codebase for better green practices.")

    if any(i.get('severity') == 'high' for i in results['issues']):
        insights.append("Critical high-severity issues found. Prioritize fixing these for maximum energy savings.")

    scanning_emissions = results.get('scanning_emissions', 0)
    if scanning_emissions > 0.00001:
        insights.append("Scan process emissions are notable. Consider optimizing scanning frequency or hardware.")

    codebase_emissions = results.get('codebase_emissions', 0)
    if codebase_emissions > 0.000001:
        insights.append(f"Estimated codebase emissions are {codebase_emissions:.9f} kg CO₂. Fixing the high-severity issues will reduce this impact.")

    total_emissions = scanning_emissions + codebase_emissions
    if codebase_emissions > scanning_emissions * 10:
        insights.append("Codebase emissions significantly exceed scanning emissions. Focus on optimizing the analyzed code.")

    return insights
