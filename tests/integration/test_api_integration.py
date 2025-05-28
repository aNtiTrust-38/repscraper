def test_api_integration():
    """Test API integration and recovery from failure"""
    assert False, "API integration test not implemented yet"

def test_health_check_endpoint():
    import requests
    import subprocess
    import time

    # Start the health check server in a subprocess
    proc = subprocess.Popen(['python3', 'src/main.py'])
    time.sleep(2)  # Give it time to start

    try:
        resp = requests.get('http://localhost:8000/health')
        assert resp.status_code == 200
        assert 'ok' in resp.text.lower()
    finally:
        proc.terminate()

def test_env_var_validation(monkeypatch):
    import subprocess
    import sys
    import os

    # Remove a required env var
    env = os.environ.copy()
    env.pop('REDDIT_CLIENT_ID', None)
    proc = subprocess.Popen([sys.executable, 'src/main.py'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(timeout=5)
    assert proc.returncode != 0
    assert b'REDDIT_CLIENT_ID' in err or b'REDDIT_CLIENT_ID' in out

def test_error_logging_to_file(tmp_path, monkeypatch):
    import subprocess
    import sys
    import os
    import time

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "app.log"
    env = os.environ.copy()
    env['LOG_FILE'] = str(log_file)
    env['REDDIT_CLIENT_ID'] = ''  # Force validation error
    env['REDDIT_CLIENT_SECRET'] = 'x'
    env['REDDIT_USER_AGENT'] = 'x'
    env['TELEGRAM_BOT_TOKEN'] = 'x'
    env['TELEGRAM_CHAT_ID'] = 'x'
    proc = subprocess.Popen([sys.executable, 'src/main.py'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate(timeout=5)
    time.sleep(0.5)  # Give loguru time to flush
    assert log_file.exists()
    with open(log_file) as f:
        log_content = f.read()
    assert 'REDDIT_CLIENT_ID' in log_content

def test_no_secrets_in_logs(tmp_path, monkeypatch):
    import subprocess
    import sys
    import os
    import time

    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "app.log"
    env = os.environ.copy()
    # Set secrets to known values
    env['LOG_FILE'] = str(log_file)
    env['REDDIT_CLIENT_ID'] = 'SECRET_CLIENT_ID'
    env['REDDIT_CLIENT_SECRET'] = 'SECRET_CLIENT_SECRET'
    env['REDDIT_USER_AGENT'] = 'SECRET_USER_AGENT'
    env['TELEGRAM_BOT_TOKEN'] = 'SECRET_BOT_TOKEN'
    env['TELEGRAM_CHAT_ID'] = 'SECRET_CHAT_ID'
    # Force a validation error by removing one required var
    env['REDDIT_CLIENT_ID'] = ''
    proc = subprocess.Popen([sys.executable, 'src/main.py'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate(timeout=5)
    time.sleep(0.5)
    assert log_file.exists()
    with open(log_file) as f:
        log_content = f.read()
    # None of the secret values should appear in the log
    assert 'SECRET_CLIENT_SECRET' not in log_content
    assert 'SECRET_USER_AGENT' not in log_content
    assert 'SECRET_BOT_TOKEN' not in log_content
    assert 'SECRET_CHAT_ID' not in log_content
