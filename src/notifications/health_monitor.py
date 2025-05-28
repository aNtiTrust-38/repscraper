import requests
from loguru import logger
import threading
import os
import time

def send_telegram_alert(message: str, token: str, chat_id: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info(f"Sent Telegram alert to chat_id={chat_id}: {message}")
        else:
            logger.error(f"Failed to send Telegram alert: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Exception sending Telegram alert: {e}")

def run_health_check() -> None:
    """Example health check: check DB connectivity, API, etc. Raise on failure."""
    logger.info("Starting health check...")
    # Placeholder: simulate healthy
    # To simulate failure, raise Exception('Health check failed')
    # In real use, check DB, API, etc.
    logger.info("Health check passed.")
    pass

def start_periodic_health_check(interval_sec: int = 60):
    """Start periodic health check in a background thread."""
    def periodic():
        logger.info("Running scheduled health check...")
        try:
            run_health_check()
        except Exception as e:
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            logger.error(f"Health check failed: {e}")
            if token and chat_id:
                send_telegram_alert(f"Health check failed: {e}", token, chat_id)
        finally:
            # Schedule next check
            threading.Timer(interval_sec, periodic).start()
    logger.info(f"Starting periodic health check every {interval_sec} seconds.")
    periodic()

if __name__ == "__main__":
    start_periodic_health_check()
    while True:
        time.sleep(60)
