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
