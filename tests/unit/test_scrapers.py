import pytest

def test_reddit_scraper_initialization():
    """Test that RedditScraper initializes with valid config
    Requirements from instructions.md:
    - Must use dedicated Reddit account (not personal)
    - Must support 2-hour batch processing  
    - Must respect rate limits (60 requests/minute)
    """
    config = {
        'client_id': 'test_id',
        'client_secret': 'test_secret', 
        'user_agent': 'test_agent'
    }
    
    from src.scrapers.reddit_scraper import RedditScraper
    scraper = RedditScraper(config)
    assert scraper is not None
    assert scraper.config == config
    assert scraper.batch_interval_hours == 2  # From instructions.md requirement

def test_extract_links_priority_matrix():
    """Test extraction of links from all top 5 platforms with correct priority order
    Per instructions.md MVP: Taobao, Weidian, 1688, Yupoo, Pandabuy
    """
    from src.scrapers.link_extractor import LinkExtractor
    text = (
        "Taobao: https://item.taobao.com/item.htm?id=123456789 "
        "Weidian: https://weidian.com/item.html?id=987654321 "
        "1688: https://detail.1688.com/offer/11223344.html "
        "Yupoo: https://x.yupoo.com/albums/55667788 "
        "Pandabuy: https://pandabuy.com/item/99887766 "
    )
    extractor = LinkExtractor()
    links = extractor.extract_links(text)
    assert len(links) == 5
    assert links[0]['platform'] == 'taobao'
    assert links[1]['platform'] == 'weidian'
    assert links[2]['platform'] == '1688'
    assert links[3]['platform'] == 'yupoo'
    assert links[4]['platform'] == 'pandabuy'
    # Check priorities (lower is higher priority)
    assert links[0]['priority'] == 1
    assert links[1]['priority'] == 2
    assert links[2]['priority'] == 3
    assert links[3]['priority'] == 4
    assert links[4]['priority'] == 6  # Pandabuy always last
