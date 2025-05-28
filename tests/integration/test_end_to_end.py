def test_end_to_end_workflow():
    from src.scrapers.link_extractor import LinkExtractor
    from src.processors.quality_filter import basic_filter, calculate_quality_score
    from src.database.crud import PersistentDeduper
    from src.notifications.telegram_bot import format_simple_message
    import tempfile

    # Simulate a new post
    post = {
        'id': 'abc123',
        'title': 'Great Find',
        'author': {'link_karma': 1000, 'name': 'testuser'},
        'upvotes': 20,
        'num_comments': 5,
        'created_utc': __import__('datetime').datetime.utcnow(),
        'selftext': 'A detailed review of a great item.' * 10,
        'image_urls': ['img1.jpg'],
        'all_awardings': [1],
        'platform': 'taobao',
        'url': 'https://item.taobao.com/item.htm?id=123456789'
    }
    # Deduplication
    with tempfile.NamedTemporaryFile() as tf:
        deduper = PersistentDeduper(tf.name)
        assert not deduper.is_duplicate(post['id'])
        deduper.mark_processed(post['id'])
        assert deduper.is_duplicate(post['id'])

    # Filtering
    filtered = basic_filter([{
        'id': post['id'],
        'upvotes': post['upvotes'],
        'comments': post['num_comments'],
        'created_utc': post['created_utc']
    }], min_upvotes=5, min_comments=2, max_age_hours=24, now=post['created_utc'])
    assert len(filtered) == 1

    # Quality scoring
    score = calculate_quality_score(post)
    assert score > 0.3

    # Notification formatting
    msg = format_simple_message({
        'title': post['title'],
        'author': post['author']['name'],
        'upvotes': post['upvotes'],
        'comments': post['num_comments'],
        'platform': post['platform'],
        'url': post['url']
    })
    assert 'Great Find' in msg
    assert 'testuser' in msg
    assert 'https://item.taobao.com/item.htm?id=123456789' in msg

def test_end_to_end_flair_filtering():
    """End-to-end: Only posts with allowed flairs are notified."""
    from src.processors.quality_filter import filter_by_flair
    allowed_flairs = ['QC', 'Haul', 'Review']
    posts = [
        {'id': '1', 'flair': 'QC', 'upvotes': 10, 'comments': 3, 'created_utc': 0},      # Pass
        {'id': '2', 'flair': 'Haul', 'upvotes': 5, 'comments': 2, 'created_utc': 0},     # Pass
        {'id': '3', 'flair': 'W2C', 'upvotes': 8, 'comments': 2, 'created_utc': 0},      # Fail (not allowed)
        {'id': '4', 'flair': 'Review', 'upvotes': 7, 'comments': 2, 'created_utc': 0},   # Pass
        {'id': '5', 'flair': '', 'upvotes': 6, 'comments': 2, 'created_utc': 0},         # Fail (no flair)
    ]
    filtered = filter_by_flair(posts, allowed_flairs)
    assert len(filtered) == 3
    assert all(post['flair'] in allowed_flairs for post in filtered)

def test_batch_processing_workflow(mocker):
    """Test batch processing: scrapes, filters, deduplicates, and notifies only new, relevant posts."""
    # Mock scraping: return a batch of posts (some new, some duplicate, some irrelevant)
    posts = [
        {'id': '1', 'flair': 'QC', 'upvotes': 10, 'comments': 3, 'created_utc': 0, 'author': 'user1', 'title': 'QC Shoes', 'platform': 'taobao', 'url': 'https://item.taobao.com/item.htm?id=1'},  # New, relevant
        {'id': '2', 'flair': 'Haul', 'upvotes': 5, 'comments': 2, 'created_utc': 0, 'author': 'user2', 'title': 'Haul Bag', 'platform': 'weidian', 'url': 'https://weidian.com/item.html?id=2'},  # New, relevant
        {'id': '3', 'flair': 'W2C', 'upvotes': 8, 'comments': 2, 'created_utc': 0, 'author': 'user3', 'title': 'W2C Shirt', 'platform': '1688', 'url': 'https://detail.1688.com/offer/3.html'},  # Irrelevant flair
        {'id': '4', 'flair': 'QC', 'upvotes': 2, 'comments': 1, 'created_utc': 0, 'author': 'user4', 'title': 'Low Upvotes', 'platform': 'yupoo', 'url': 'https://x.yupoo.com/albums/4'},  # Fails filter
        {'id': '5', 'flair': 'QC', 'upvotes': 10, 'comments': 3, 'created_utc': 0, 'author': 'user5', 'title': 'Duplicate', 'platform': 'pandabuy', 'url': 'https://pandabuy.com/item/5'},  # Duplicate
    ]
    allowed_flairs = ['QC', 'Haul', 'Review']
    min_upvotes = 5
    min_comments = 2
    # Mock deduplication: post '5' is already processed
    processed_ids = {'5'}
    def is_duplicate(post_id):
        return post_id in processed_ids
    # Mock notification: capture sent messages
    sent = []
    class MockBot:
        def send_item_notification(self, item):
            sent.append(item['id'])
    # Simulate batch processing logic
    from src.processors.quality_filter import filter_by_flair, basic_filter
    # 1. Flair filter
    filtered = filter_by_flair(posts, allowed_flairs)
    # 2. Quality filter
    filtered = basic_filter(filtered, min_upvotes, min_comments, max_age_hours=24, now=0)
    # 3. Deduplication
    filtered = [p for p in filtered if not is_duplicate(p['id'])]
    # 4. Notification
    bot = MockBot()
    for post in filtered:
        bot.send_item_notification(post)
    # Assert only new, relevant, non-duplicate posts are notified
    assert set(sent) == {'1', '2'}
