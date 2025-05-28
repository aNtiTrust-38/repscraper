import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
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

def format_simple_message(item):
    return (
        f"{item['title']}\n"
        f"By: {item['author']} | {item['upvotes']}⬆️ | {item['comments']}💬\n"
        f"Platform: {item['platform'].title()}\n"
        f"Link: {item['url']}"
    )
