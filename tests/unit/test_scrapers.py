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
