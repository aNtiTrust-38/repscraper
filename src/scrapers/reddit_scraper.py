import praw

class RedditScraper:
    def __init__(self, config):
        self.config = config
        self.batch_interval_hours = config.get('batch_interval_hours', 2)
        self.subreddits = config.get('subreddits', ['FashionReps'])
        self.max_posts_per_batch = config.get('max_posts_per_batch', 5)
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.user_agent = config['user_agent']
        self._init_client()

    def _init_client(self):
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
        except Exception as e:
            raise RuntimeError(f"Reddit API authentication failed: {e}")

    def fetch_batch(self):
        try:
            posts = []
            for subreddit in self.subreddits:
                submissions = self.reddit.subreddit(subreddit).new(limit=self.max_posts_per_batch)
                for submission in submissions:
                    posts.append({
                        'id': submission.id,
                        'title': submission.title,
                        'url': submission.url
                    })
            if len(posts) < self.max_posts_per_batch:
                # Pad with None or raise if strict
                pass
            return posts[:self.max_posts_per_batch]
        except Exception as e:
            raise RuntimeError(f"Reddit API fetch failed: {e}")
