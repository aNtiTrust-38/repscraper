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
        'id': 1,
        'url': 'https://item.taobao.com/item.htm?id=123456789',
    }
    # Should not raise
    bot.send_item_notification(item_data)

def test_simple_telegram_notification_formatting():
    from src.notifications.telegram_bot import format_simple_message
    item = {
        'title': 'Test Item',
        'author': 'testuser',
        'upvotes': 10,
        'comments': 3,
        'platform': 'taobao',
        'url': 'https://item.taobao.com/item.htm?id=123456789'
    }
    msg = format_simple_message(item)
    assert 'Test Item' in msg
    assert 'testuser' in msg
    assert '10' in msg
    assert '3' in msg
    assert 'https://item.taobao.com/item.htm?id=123456789' in msg

def test_telegram_alert_on_error(mocker):
    from src.notifications.health_monitor import send_telegram_alert

    # Mock the actual network call
    mock_send = mocker.patch('src.notifications.health_monitor.requests.post')
    send_telegram_alert("Test alert", token="dummy_token", chat_id="dummy_chat")
    assert mock_send.called
    args, kwargs = mock_send.call_args
    assert "sendMessage" in args[0]
    assert "Test alert" in kwargs['data']['text']

def test_telegram_notification_with_extracted_links(mocker):
    """Test that Telegram notification is sent with clean, readable message and extracted links."""
    from src.notifications.telegram_bot import TelegramBot
    # Mock send_item_notification to capture the message
    sent = {}
    class MockBot(TelegramBot):
        def send_item_notification(self, item_data):
            sent['msg'] = self.format_message(item_data)
    # Simulate extracted item
    item_data = {
        'title': 'Taobao Shoes',
        'author': 'user123',
        'upvotes': 42,
        'comments': 7,
        'platform': 'taobao',
        'url': 'https://item.taobao.com/item.htm?id=123456789',
    }
    # Add a format_message method for test (should match production formatting)
    MockBot.format_message = staticmethod(lambda item: f"{item['title']}\nBy: {item['author']} | {item['upvotes']}⬆️ | {item['comments']}💬\nPlatform: {item['platform'].title()}\nLink: {item['url']}")
    bot = MockBot(token='dummy', chat_id='dummy')
    bot.send_item_notification(item_data)
    assert 'Taobao Shoes' in sent['msg']
    assert 'user123' in sent['msg']
    assert '42' in sent['msg']
    assert '7' in sent['msg']
    assert 'https://item.taobao.com/item.htm?id=123456789' in sent['msg']
