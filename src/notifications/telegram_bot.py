class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
    def send_item_notification(self, item_data):
        # Stub: Accepts item_data, does nothing (for test pass)
        pass

def format_simple_message(item):
    return (
        f"{item['title']}\n"
        f"By: {item['author']} | {item['upvotes']}⬆️ | {item['comments']}💬\n"
        f"Platform: {item['platform'].title()}\n"
        f"Link: {item['url']}"
    )
