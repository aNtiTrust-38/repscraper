def test_telegram_message_formatting():
    """Test rich message generation and sending"""
    from src.notifications.telegram_bot import TelegramBot
    bot = TelegramBot(token='dummy', chat_id='dummy')
    item_data = {
        'title': 'Test Item',
        'author': 'testuser',
        'upvotes': 10,
        'comments': 3,
        'price_cny': 100,
        'price_usd': 15,
        'platform': 'taobao',
        'priority': 1,
        'description': 'A great item',
        'time_ago': '1 hour ago',
        'images_url': 'https://imgur.com/test',
        'converted_url': 'https://jadeship.com/converted',
        'thumbnail_url': 'https://imgur.com/thumb.jpg',
        'id': 1
    }
    # Should not raise
    bot.send_item_notification(item_data)
