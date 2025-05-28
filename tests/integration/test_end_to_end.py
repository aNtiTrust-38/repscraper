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
