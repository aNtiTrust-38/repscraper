import datetime

def test_jadeship_conversion():
    """Test link conversion with agent priority"""
    from src.processors.link_converter import JadeshipConverter
    converter = JadeshipConverter()
    result = converter.convert_link('https://item.taobao.com/item.htm?id=123456789')
    assert result['agent_used'] == 'allchinabuy'  # Should use primary agent
    assert result['success'] is True

def test_basic_post_filtering():
    now = datetime.datetime.utcnow()
    posts = [
        {'id': '1', 'upvotes': 10, 'comments': 3, 'created_utc': now - datetime.timedelta(hours=1)},  # Pass
        {'id': '2', 'upvotes': 2, 'comments': 3, 'created_utc': now - datetime.timedelta(hours=1)},   # Fail (upvotes)
        {'id': '3', 'upvotes': 10, 'comments': 1, 'created_utc': now - datetime.timedelta(hours=1)},  # Fail (comments)
        {'id': '4', 'upvotes': 10, 'comments': 3, 'created_utc': now - datetime.timedelta(hours=25)}, # Fail (age)
    ]
    from src.processors.quality_filter import basic_filter
    filtered = basic_filter(posts, min_upvotes=5, min_comments=2, max_age_hours=24, now=now)
    assert len(filtered) == 1
    assert filtered[0]['id'] == '1'

def test_quality_scoring():
    from src.processors.quality_filter import calculate_quality_score
    post = {
        'upvotes': 50,
        'num_comments': 10,
        'author': {'link_karma': 5000},
        'image_urls': ['img1.jpg'],
        'selftext': 'A detailed review of a great item.' * 10,
        'all_awardings': [1, 2],
    }
    score = calculate_quality_score(post)
    assert 0 <= score <= 1
    # Should be high due to good engagement, author, content, and awards
    assert score > 0.7
