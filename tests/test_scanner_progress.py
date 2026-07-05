from src.core.scanner.main import Scanner
import os
import tempfile


def test_scanner_progress_updates():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple files to ensure multiple progress updates
        for i in range(5):
            with open(os.path.join(tmpdir, f'file{i}.py'), 'w') as f:
                f.write('print("hello")')

        progress_calls = []

        def progress_callback(message, percentage):
            progress_calls.append((message, percentage))

        scanner = Scanner(language='python')
        scanner.scan(tmpdir, progress_callback=progress_callback)

        # Check if callback was called
        assert len(progress_calls) >= 7  # 1 (Start) + 5 (Files) + 1 (Finalizing) + 1 (Complete)

        # Check for start message
        assert any("Scanning files..." in call[0] for call in progress_calls)
        # Check for file processing messages
        assert any("Processing file0.py" in call[0] for call in progress_calls)
        # Check for completion
        assert progress_calls[-1][1] == 100
        assert "Scan complete" in progress_calls[-1][0]
