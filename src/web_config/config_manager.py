import yaml
import os
from src.web_config.models import ConfigModel
from typing import Any
import shutil

CONFIG_PATH = "src/config/config.yaml"
BACKUP_PATH = "src/config/config.yaml.bak"

def load_config() -> ConfigModel:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
    try:
        return ConfigModel.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid config format: {e}")

def save_config(config: ConfigModel) -> None:
    # Backup current config
    if os.path.exists(CONFIG_PATH):
        try:
            os.replace(CONFIG_PATH, BACKUP_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to backup config: {e}")
    # Write atomically
    tmp_path = CONFIG_PATH + ".tmp"
    with open(tmp_path, "w") as f:
        yaml.safe_dump(config.model_dump(), f, sort_keys=False, allow_unicode=True)
    os.chmod(tmp_path, 0o600)
    os.replace(tmp_path, CONFIG_PATH)

def backup_config() -> None:
    """Atomically back up config.yaml to config.yaml.bak."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    try:
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
        os.chmod(BACKUP_PATH, 0o600)
    except Exception as e:
        raise RuntimeError(f"Failed to back up config: {e}")

def restore_config() -> None:
    """Atomically restore config.yaml from config.yaml.bak."""
    if not os.path.exists(BACKUP_PATH):
        raise FileNotFoundError(f"Backup file not found: {BACKUP_PATH}")
    try:
        shutil.copy2(BACKUP_PATH, CONFIG_PATH)
        os.chmod(CONFIG_PATH, 0o600)
    except Exception as e:
        raise RuntimeError(f"Failed to restore config: {e}") 