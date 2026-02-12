"""
Green AI Agent Dashboard Server

This module acts as the entry point for the dashboard application.
It handles eventlet patching before importing the Flask application
to ensure proper concurrency.
"""

def run_dashboard():
    """Run the Green AI Agent Dashboard"""
    import eventlet
    # Patch eventlet as early as possible
    eventlet.monkey_patch()
    
    # Import app after patching
    from src.ui.dashboard_app import app, socketio, initialize_app
    
    # Initialize application state
    initialize_app()

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
    
    # Use socketio.run instead of app.run for eventlet support
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    run_dashboard()
