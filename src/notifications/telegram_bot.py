import requests
import threading
import time
from loguru import logger

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.last_update_id = None
        self.running = False
        self.poll_thread = None
        
    def send_item_notification(self, item_data):
        message = self.format_message(item_data)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        requests.post(url, data=data)
        
    @staticmethod
    def format_message(item):
        return format_simple_message(item)
    
    def send_message(self, text):
        """Send a simple text message to the configured chat_id."""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        response = requests.post(url, data=data)
        return response.json()
    
    def get_updates(self, offset=None, timeout=30):
        """Poll for updates from Telegram."""
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {
            'offset': offset,
            'timeout': timeout
        }
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return {"ok": False, "error": str(e)}
    
    def handle_command(self, update):
        """Process commands received from Telegram."""
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        # Only process commands from the configured chat_id
        if str(chat_id) != str(self.chat_id):
            logger.warning(f"Received command from unauthorized chat_id: {chat_id}")
            return
        
        if text == '/run-batch':
            logger.info("Received /run-batch command")
            self.send_message("Starting batch processing...")
            try:
                # Import here to avoid circular imports
                from src.main import run_batch
                run_batch()
                self.send_message("✅ Batch processing completed successfully")
            except Exception as e:
                error_message = f"❌ Error during batch processing: {str(e)}"
                logger.error(error_message)
                self.send_message(error_message)
        
        elif text == '/status':
            logger.info("Received /status command")
            try:
                # Import here to avoid circular imports
                from src.database.crud import PersistentDeduper
                deduper = PersistentDeduper('data/fashionreps.db')
                stats = deduper.get_stats()
                
                status_message = (
                    "📊 *System Status*\n"
                    f"- Bot is active and listening for commands\n"
                    f"- Total processed posts: {stats.get('total_processed', 0)}\n"
                    f"- Posts processed today: {stats.get('processed_today', 0)}\n"
                    f"- Last batch run: {stats.get('last_run', 'Never')}\n"
                )
                self.send_message(status_message)
            except Exception as e:
                error_message = f"❌ Error getting status: {str(e)}"
                logger.error(error_message)
                self.send_message(error_message)
        
        elif text.startswith('/'):
            # Handle unknown commands
            self.send_message(f"Unknown command: {text}\n\nAvailable commands:\n/run-batch - Run a scraping batch now\n/status - Check system status")
    
    def start_polling(self, poll_interval=5):
        """Start polling for updates in a background thread."""
        if self.running:
            logger.warning("Bot is already polling for updates")
            return
        
        self.running = True
        
        def polling_thread():
            logger.info("Starting Telegram bot polling thread")
            while self.running:
                try:
                    updates = self.get_updates(offset=self.last_update_id)
                    if updates.get("ok", False):
                        results = updates.get("result", [])
                        if results:
                            # Process all updates
                            for update in results:
                                self.handle_command(update)
                                # Update the last_update_id to acknowledge this update
                                self.last_update_id = update["update_id"] + 1
                    else:
                        logger.error(f"Failed to get updates: {updates.get('description', 'Unknown error')}")
                except Exception as e:
                    logger.error(f"Error in polling thread: {e}")
                
                time.sleep(poll_interval)
        
        # Start the polling in a background thread
        self.poll_thread = threading.Thread(target=polling_thread, daemon=True)
        self.poll_thread.start()
        logger.info("Telegram bot polling thread started")
    
    def stop_polling(self):
        """Stop the polling thread."""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=5)
            logger.info("Telegram bot polling thread stopped")

def format_simple_message(item):
    return (
        f"{item['title']}\n"
        f"By: {item['author']} | {item['upvotes']}⬆️ | {item['comments']}💬\n"
        f"Platform: {item['platform'].title()}\n"
        f"Link: {item['url']}"
    )
