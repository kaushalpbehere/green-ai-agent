"""
Dashboard module for Green AI Agent
"""

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.standards.registry import StandardsRegistry
from src.ui.charts import generate_all_charts
from src.core.project_manager import ProjectManager
from src.core.history import HistoryManager
from src.core.scanner import Scanner
from src.core.remediation import RemediationAgent
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store last scan results
last_scan_results = None
last_charts = None
standards_registry = StandardsRegistry()
project_manager = ProjectManager()
history_manager = HistoryManager()
remediation_agent = RemediationAgent()


def broadcast_progress(message, percentage):
    """Broadcast scan progress to all connected clients."""
    socketio.emit('scan_progress', {'message': message, 'percentage': percentage})

# Ensure default project exists on startup and trigger initial scan if needed
try:
    default_project = project_manager.get_project("Green-AI Agent")
    # Force use the local path for the default project
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    if not default_project:
        project_manager.add_project(
            name="Green-AI Agent",
            repo_url=root_dir,
            branch="main",
            language="python",
            is_system=True
        )
        print(f"Initialized default project at {root_dir}")
        
    # Trigger initial scan in background if last_scan is None
    default_project = project_manager.get_project("Green-AI Agent")
    if default_project and not default_project.last_scan:
        print("Triggering initial background scan for Green-AI Agent...")
        def initial_scan():
            try:
                scanner = Scanner(language="python")
                results = scanner.scan(root_dir)
                set_last_scan_results(results)
                history_manager.add_scan("Green-AI Agent", results)
                project_manager.update_project_scan("Green-AI Agent", len(results['issues']), results.get('total_emissions', 0))
                print("Initial scan completed.")
            except Exception as e:
                print(f"Initial scan failed: {e}")
        
        scan_thread = threading.Thread(target=initial_scan)
        scan_thread.daemon = True
        scan_thread.start()
except Exception as e:
    print(f"Warning: Could not initialize default project: {e}")

def set_last_scan_results(results):
    global last_scan_results, last_charts
    last_scan_results = results
    last_charts = generate_all_charts(results)

def calculate_average_grade(projects):
    """Calculate average grade from projects"""
    if not projects:
        return "N/A"
    
    grades = {
        'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1
    }
    
    total_score = sum(grades.get(p.get_grade(), 0) for p in projects)
    avg_score = total_score / len(projects)
    
    # Convert back to grade
    for grade, score in sorted(grades.items(), key=lambda x: x[1], reverse=True):
        if avg_score >= score:
            return grade
    
    return "F"

@app.route('/')
def dashboard():
    if last_scan_results:
        insights = generate_insights(last_scan_results)
        return render_template_string(DASHBOARD_HTML, results=last_scan_results, insights=insights, charts=last_charts)
    else:
        # Show enhanced landing page with stats
        projects = project_manager.list_projects()
        total_violations = sum(p.latest_violations for p in projects)
        avg_grade = calculate_average_grade(projects) if projects else "N/A"
        recent_projects = sorted(projects, key=lambda p: p.last_scan or "", reverse=True)[:5]
        
        return render_template_string(LANDING_PAGE_HTML, 
                                     projects=projects,
                                     total_violations=total_violations,
                                     avg_grade=avg_grade,
                                     recent_projects=recent_projects,
                                     project_count=len(projects))
        
@app.route('/api/charts')
def api_charts():
    """Return all chart data as JSON"""
    return json.dumps(last_charts) if last_charts else json.dumps({})

@app.route('/api/results')
def api_results():
    return json.dumps(last_scan_results) if last_scan_results else json.dumps({})

# Standards API Endpoints
@app.route('/api/standards')
def api_standards_list():
    """List all available standards"""
    return jsonify(standards_registry.list_standards())

@app.route('/api/standards/<standard_name>/enable', methods=['POST'])
def api_enable_standard(standard_name):
    """Enable a standard"""
    standards_registry.enable_standard(standard_name)
    return jsonify({'status': 'ok', 'message': f'Standard {standard_name} enabled'})

@app.route('/api/standards/<standard_name>/disable', methods=['POST'])
def api_disable_standard(standard_name):
    """Disable a standard"""
    standards_registry.disable_standard(standard_name)
    return jsonify({'status': 'ok', 'message': f'Standard {standard_name} disabled'})

@app.route('/api/standards/<standard_name>/rules')
def api_standard_rules(standard_name):
    """Get rules for a specific standard"""
    if standard_name in standards_registry.standards:
        rules = standards_registry.standards[standard_name]
        return jsonify({
            'standard': standard_name,
            'rule_count': len(rules),
            'rules': [{'id': r.id, 'name': r.name, 'severity': r.severity} for r in rules]
        })
    return jsonify({'error': 'Standard not found'}), 404

@app.route('/api/rules/<rule_id>/disable', methods=['POST'])
def api_disable_rule(rule_id):
    """Disable a specific rule"""
    standards_registry.disable_rule(rule_id)
    return jsonify({'status': 'ok', 'message': f'Rule {rule_id} disabled'})

@app.route('/api/rules/<rule_id>/enable', methods=['POST'])
def api_enable_rule(rule_id):
    """Enable a specific rule"""
    standards_registry.enable_rule(rule_id)
    return jsonify({'status': 'ok', 'message': f'Rule {rule_id} enabled'})

@app.route('/api/standards/export/<format>')
def api_export_rules(format):
    """Export rules in specified format"""
    if format == 'json':
        return standards_registry.export_rules_json()
    elif format == 'yaml':
        return standards_registry.export_rules_yaml()
    else:
        return jsonify({'error': 'Invalid format'}), 400


# Projects API Endpoints
@app.route('/api/projects')
def api_projects_list():
    """List all projects with their metrics"""
    projects = project_manager.list_projects()
    
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
            'average_grade': calculate_average_grade(projects),
            'combined_emissions': sum(p['total_emissions'] for p in projects_data),
        }
    })

@app.route('/api/projects/<project_name>')
def api_project_detail(project_name):
    """Get detailed view of a single project"""
    project = project_manager.get_project(project_name)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    project_dict = project.to_dict()
    project_dict['health_grade'] = project.get_grade()
    project_dict['violations'] = [] # Need to load from history if needed
    
    return jsonify({
        'status': 'ok',
        'project': project_dict
    })

@app.route('/api/projects/comparison')
def api_projects_comparison():
    """Get comparison data for multiple projects"""
    # Get project names from query params
    project_names = request.args.getlist('projects')
    
    if not project_names or len(project_names) == 0:
        return jsonify({'error': 'No projects specified. Use ?projects=name1&projects=name2'}), 400
    
    if len(project_names) > 5:
        return jsonify({'error': 'Maximum 5 projects can be compared at once'}), 400
    
    comparison_data = []
    for project_name in project_names:
        project = project_manager.get_project(project_name)
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
def api_scan():
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
    
    # Check if project exists, create if not
    existing = project_manager.get_project(project_name)
    if not existing:
        project_manager.add_project(project_name, repo_url=git_url or path, language=language)
    
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
            history_manager.add_scan(project_name, results)
            
            broadcast_progress("Scan complete!", 100)
            socketio.emit('scan_finished', {'project_name': project_name})
            
        except Exception as e:
            print(f"Background scan error: {e}")
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
def api_delete_project(project_name):
    """Delete a project"""
    try:
        project = project_manager.get_project(project_name)
        if not project:
            return jsonify({'error': f'Project {project_name} not found'}), 404
        
        if project.is_system:
            return jsonify({'error': f'Cannot delete system project: {project_name}'}), 403
        
        project_manager.remove_project(project_name)
        return jsonify({
            'status': 'ok',
            'message': f'Project {project_name} deleted'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/projects/<project_name>/rescan', methods=['POST'])
def api_rescan_project(project_name):
    """Rescan an existing project"""
    try:
        project = project_manager.get_project(project_name)
        
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
def api_clear_project(project_name):
    """Clear violations and rescan project"""
    try:
        project = project_manager.get_project(project_name)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Clear violations
        # Reset fields if needed (Project object doesn't have violations list directly)
        project.latest_violations = 0
        project.total_emissions = 0.0
        project_manager._save_projects()
        
        return jsonify({
            'status': 'ok',
            'message': f'Project {project_name} cleared and ready for rescan'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to clear project: {str(e)}'}), 500


@app.route('/api/export/csv', methods=['GET'])
def api_export_csv():
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
def api_export_html():
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
def api_get_history():
    """Get historical scan data for a project"""
    try:
        project_name = request.args.get('project')
        days = request.args.get('days', type=int, default=None)
        
        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400
        
        scans = history_manager.get_project_history(project_name, days=days)
        
        return jsonify({
            'project': project_name,
            'scans': [s.to_dict() for s in scans],
            'count': len(scans)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500


@app.route('/api/trending', methods=['GET'])
def api_get_trending():
    """Get trending analysis for a project"""
    try:
        project_name = request.args.get('project')
        days = request.args.get('days', type=int, default=None)
        
        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400
        
        trending = history_manager.get_trending_data(project_name, days=days)
        
        return jsonify({
            'project': project_name,
            'trend': trending['trend'],
            'details': trending,
            'grade_improvement': trending.get('grade_improvement', 'N/A')
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get trending: {str(e)}'}), 500


@app.route('/api/compare', methods=['GET'])
def api_compare_scans():
    """Compare two scans in project history"""
    try:
        project_name = request.args.get('project')
        scan1_idx = request.args.get('scan1', type=int, default=-2)
        scan2_idx = request.args.get('scan2', type=int, default=-1)
        
        if not project_name:
            return jsonify({'error': 'project parameter required'}), 400
        
        scans = history_manager.get_project_history(project_name)
        
        if len(scans) < 2:
            return jsonify({'error': 'Not enough scans to compare'}), 400
        
        scan1 = scans[scan1_idx] if scan1_idx < len(scans) else scans[0]
        scan2 = scans[scan2_idx] if scan2_idx < len(scans) else scans[-1]
        
        comparison = history_manager.compare_scans(scan1, scan2)
        
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
def api_remediation_preview():
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
            
        diff = remediation_agent.get_remediation_diff(file_path, line, issue_id, content)
        description = remediation_agent.get_fix_description(issue_id)
        
        return jsonify({
            'status': 'ok',
            'diff': diff,
            'description': description
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_average_grade(grades):
    """Calculate average grade from list of letter grades"""
    if not grades:
        return 'N/A'
    
    grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
    grade_points = [grade_values.get(g, 0) for g in grades if g in grade_values]
    
    if not grade_points:
        return 'N/A'
    
    avg = sum(grade_points) / len(grade_points)
    
    if avg >= 4.5:
        return 'A'
    elif avg >= 3.5:
        return 'B'
    elif avg >= 2.5:
        return 'C'
    elif avg >= 1.5:
        return 'D'
    else:
        return 'F'



def load_template(name):
    path = os.path.join(os.path.dirname(__file__), 'templates', name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

LANDING_PAGE_HTML = load_template('landing.html')

DASHBOARD_HTML = load_template('dashboard.html')

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

def run_dashboard():
    import logging
    from pathlib import Path
    
    # Configure Flask logging to output/logs
    logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Disable Flask's default logger to prevent duplicate logs
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Configure file handler
    handler = logging.FileHandler(logs_dir / 'server.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)
    
    app.run(debug=False, port=5000, use_reloader=False)

if __name__ == '__main__':
    import logging
    from pathlib import Path
    
    # Configure Flask logging to output/logs
    logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Disable Flask's default logger
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Configure file handler
    handler = logging.FileHandler(logs_dir / 'server.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)
    
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)