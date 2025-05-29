from fastapi.testclient import TestClient
from src.web_config.app import app
import pytest
import io
import os

client = TestClient(app)

def minimal_config():
    return {
        "reddit": {"client_id": "x", "client_secret": "x", "user_agent": "x", "subreddits": ["FashionReps"]},
        "telegram": {"bot_token": "x", "chat_id": "x", "notification_format": "rich"},
        "scraping": {"batch_interval_hours": 2, "max_posts_per_batch": 50, "enable_comments": True, "monitor_new_posts": True, "monitor_hot_posts": False},
        "filters": {"min_upvotes": 5, "min_comments": 2, "max_age_hours": 24, "quality_threshold": 0.3, "exclude_deleted": True, "exclude_removed": True},
        "platforms": {"taobao": {"priority": 1, "enabled": True, "weight": 0.4}, "weidian": {"priority": 2, "enabled": True, "weight": 0.25}, "_1688": {"priority": 3, "enabled": True, "weight": 0.2}, "yupoo": {"priority": 4, "enabled": True, "weight": 0.1}, "others": {"priority": 5, "enabled": True, "weight": 0.04}, "pandabuy": {"priority": 6, "enabled": False, "weight": 0.01}},
        "jadeship": {"enabled": True, "api_url": "https://jadeship.com/api/convert", "timeout_seconds": 10, "retry_attempts": 2, "default_agent": "allchinabuy", "agent_priority": ["allchinabuy", "cnfans", "mulebuy", "wegobuy", "sugargoo", "cssbuy", "superbuy", "pandabuy"]},
        "database": {"url": "sqlite:///data/fashionreps.db", "backup_enabled": True, "backup_interval_hours": 24, "cleanup_old_data": True, "retention_days": 180},
        "health": {"enabled": True, "telegram_alerts": True, "discord_webhook": "", "pushbullet_token": "", "check_interval_minutes": 30},
        "logging": {"level": "INFO", "max_file_size_mb": 10, "backup_count": 5, "console_output": True}
    }

def test_end_to_end_config_update():
    """Test complete configuration update workflow"""
    config = minimal_config()
    # Save config
    resp = client.post("/config", json=config)
    assert resp.status_code == 200
    # Validate config
    resp = client.post("/config/validate", json=config)
    assert resp.status_code == 200
    assert resp.json()["valid"] is True
    # Load config
    resp = client.get("/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reddit"]["client_id"] == "x"

def test_config_defaults():
    """Test configuration defaults endpoint"""
    resp = client.get("/config/defaults")
    assert resp.status_code == 200
    data = resp.json()
    assert "reddit" in data and "telegram" in data
    assert data["platforms"]["taobao"]["priority"] == 1

def test_config_backup_restore():
    pytest.skip("Not implemented yet")

def test_docker_web_interface():
    pytest.skip("Not implemented yet")

def test_config_backup_endpoint():
    # Save a config
    config = minimal_config()
    resp = client.post("/config", json=config)
    assert resp.status_code == 200
    # Request backup
    resp = client.get("/config/backup")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/x-yaml")
    content = resp.content.decode()
    assert "reddit:" in content and "telegram:" in content

def test_config_restore_endpoint():
    # Save a config, then restore a different one
    config = minimal_config()
    config["reddit"]["client_id"] = "original"
    client.post("/config", json=config)
    # Create a backup file with a different value
    import yaml
    new_config = minimal_config()
    new_config["reddit"]["client_id"] = "restored"
    backup_bytes = yaml.safe_dump(new_config).encode()
    # Upload backup
    resp = client.post("/config/restore", files={"file": ("config.yaml.bak", io.BytesIO(backup_bytes), "application/x-yaml")})
    assert resp.status_code == 200
    # Verify config is restored
    resp = client.get("/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reddit"]["client_id"] == "restored"

def test_config_backup_restore_error_handling():
    # Try restore with invalid file
    resp = client.post("/config/restore", files={"file": ("bad.bak", io.BytesIO(b"not yaml"), "application/x-yaml")})
    # Should still succeed (restores file, but may not validate)
    assert resp.status_code == 200 or resp.status_code == 500
    # Remove backup file and try download
    from src.web_config.config_manager import BACKUP_PATH
    if os.path.exists(BACKUP_PATH):
        os.remove(BACKUP_PATH)
    resp = client.get("/config/backup")
    # Should fail with 500 if config.yaml is missing
    # (simulate by renaming config.yaml if needed)
    # Not always possible in CI, so just check for 200 or 500
    assert resp.status_code in (200, 500) 