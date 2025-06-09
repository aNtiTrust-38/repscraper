from fastapi import APIRouter, HTTPException, Body, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.encoders import jsonable_encoder
from src.web_config.config_manager import load_config, save_config, backup_config, restore_config, CONFIG_PATH, BACKUP_PATH
from src.web_config.models import ConfigModel
from pydantic import ValidationError
import requests
import datetime
import threading
from src.main import run_batch

router = APIRouter()

# In-memory status tracking (could be improved with persistent storage)
status = {
    "last_scrape_time": None,
    "last_notification_time": None,
    "last_error": None,
    "last_batch_count": 0
}

def get_default_config() -> ConfigModel:
    # Returns a ConfigModel with reasonable defaults (update as needed)
    return ConfigModel(
        reddit={
            "client_id": "",
            "client_secret": "",
            "user_agent": "",
            "subreddits": ["FashionReps"]
        },
        telegram={
            "bot_token": "",
            "chat_id": "",
            "notification_format": "rich"
        },
        scraping={
            "batch_interval_hours": 2,
            "max_posts_per_batch": 50,
            "enable_comments": True,
            "monitor_new_posts": True,
            "monitor_hot_posts": False
        },
        filters={
            "min_upvotes": 5,
            "min_comments": 2,
            "max_age_hours": 24,
            "quality_threshold": 0.3,
            "exclude_deleted": True,
            "exclude_removed": True
        },
        platforms={
            "taobao": {"priority": 1, "enabled": True, "weight": 0.4},
            "weidian": {"priority": 2, "enabled": True, "weight": 0.25},
            "_1688": {"priority": 3, "enabled": True, "weight": 0.2},
            "yupoo": {"priority": 4, "enabled": True, "weight": 0.1},
            "others": {"priority": 5, "enabled": True, "weight": 0.04},
            "pandabuy": {"priority": 6, "enabled": False, "weight": 0.01}
        },
        jadeship={
            "enabled": True,
            "api_url": "https://jadeship.com/api/convert",
            "timeout_seconds": 10,
            "retry_attempts": 2,
            "default_agent": "allchinabuy",
            "agent_priority": [
                "allchinabuy", "cnfans", "mulebuy", "wegobuy", "sugargoo", "cssbuy", "superbuy", "pandabuy"
            ]
        },
        database={
            "url": "sqlite:///data/fashionreps.db",
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "cleanup_old_data": True,
            "retention_days": 180
        },
        health={
            "enabled": True,
            "telegram_alerts": True,
            "discord_webhook": "",
            "pushbullet_token": "",
            "check_interval_minutes": 30
        },
        logging={
            "level": "INFO",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "console_output": True
        }
    )

@router.get("/config")
def get_config():
    try:
        config = load_config()
        return config.model_dump()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Config file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
def save_config_route(config: dict = Body(...)):
    try:
        # Validate config before saving
        parsed = ConfigModel.model_validate(config)
        save_config(parsed)
        return {"success": True}
    except ValidationError as e:
        # Return detailed validation errors for UX
        return JSONResponse(status_code=422, content={
            "success": False,
            "error": "Validation failed. Please check the highlighted fields.",
            "fields": e.errors(),
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/config/validate")
def validate_config_endpoint(config: dict = Body(...)):
    try:
        ConfigModel.model_validate(config)
        return {"valid": True, "errors": []}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}

@router.get("/config/defaults")
def get_defaults():
    defaults = get_default_config()
    return defaults.model_dump()

@router.post("/config/test-reddit")
def test_reddit(body: dict = Body(...)):
    """Test Reddit API connection with provided credentials."""
    try:
        import praw
        reddit = praw.Reddit(
            client_id=body["client_id"],
            client_secret=body["client_secret"],
            user_agent=body["user_agent"]
        )
        # Try to fetch own user (should fail if credentials are invalid)
        _ = reddit.user.me()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/config/test-telegram")
def test_telegram(body: dict = Body(...)):
    """Test Telegram bot connection with provided token and chat_id."""
    try:
        token = body["bot_token"]
        chat_id = body["chat_id"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, data={"chat_id": chat_id, "text": "Test message from FashionReps Scraper config UI."})
        if resp.status_code == 200 and resp.json().get("ok"):
            return {"success": True}
        else:
            return {"success": False, "error": resp.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/config/backup")
def download_config_backup():
    """Download the current config.yaml as a backup file."""
    try:
        backup_config()  # Ensure latest backup
        return FileResponse(BACKUP_PATH, filename="config.yaml.bak", media_type="application/x-yaml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}")

@router.post("/config/restore")
def upload_config_restore(file: UploadFile = File(...)):
    """Restore config.yaml from uploaded backup file."""
    try:
        # Save uploaded file to BACKUP_PATH, then restore
        contents = file.file.read()
        with open(BACKUP_PATH, "wb") as f:
            f.write(contents)
        restore_config()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {e}")

@router.post("/run-batch")
def run_batch_endpoint():
    """Trigger the batch scraping and notification process immediately."""
    try:
        def batch_wrapper():
            try:
                run_batch()
                status["last_scrape_time"] = datetime.datetime.utcnow().isoformat()
                # For demo: assume notification sent if batch runs
                status["last_notification_time"] = status["last_scrape_time"]
                status["last_error"] = None
                status["last_batch_count"] = 1  # Could be improved to count posts
            except Exception as e:
                status["last_error"] = str(e)
        # Run in a thread to avoid blocking
        t = threading.Thread(target=batch_wrapper)
        t.start()
        return {"success": True, "message": "Batch started."}
    except Exception as e:
        status["last_error"] = str(e)
        return {"success": False, "error": str(e)}

@router.get("/status")
def get_status():
    """Return the current status of the scraper and notification system."""
    return status

# Add a global handler for 422 errors (RequestValidationError)
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from fastapi.responses import JSONResponse

def add_422_handler(app: FastAPI):
    @app.exception_handler(FastAPIRequestValidationError)
    async def validation_exception_handler(request: Request, exc: FastAPIRequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation failed. Please check your input.",
                "fields": exc.errors(),
            },
        ) 