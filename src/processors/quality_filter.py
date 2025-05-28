import datetime
from typing import List, Dict

def basic_filter(posts: List[Dict], min_upvotes: int, min_comments: int, max_age_hours: int, now: datetime.datetime) -> List[Dict]:
    filtered = []
    for post in posts:
        if post['upvotes'] < min_upvotes:
            continue
        if post['comments'] < min_comments:
            continue
        age_hours = (now - post['created_utc']).total_seconds() / 3600
        if age_hours > max_age_hours:
            continue
        filtered.append(post)
    return filtered

def calculate_quality_score(post: Dict) -> float:
    # Engagement metrics (40% weight)
    upvote_ratio = min(post.get('upvotes', 0) / 100, 1.0)
    comment_ratio = min(post.get('num_comments', 0) / 20, 1.0)
    engagement = (upvote_ratio + comment_ratio) * 0.4

    # Author reputation (20% weight)
    author_karma = min(post.get('author', {}).get('link_karma', 0) / 10000, 1.0)
    author_score = author_karma * 0.2

    # Content quality (20% weight)
    has_images = 1 if post.get('image_urls') and len(post['image_urls']) > 0 else 0
    detailed_text = 1 if len(post.get('selftext', '')) > 100 else 0
    content_score = (has_images + detailed_text) * 0.1

    # Community response (20% weight)
    award_count = len(post.get('all_awardings', []))
    community_score = min(award_count / 5, 1.0) * 0.2

    score = engagement + author_score + content_score + community_score
    return min(score, 1.0)
