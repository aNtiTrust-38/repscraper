import sqlite3

def is_duplicate(post_id, processed_ids):
    return post_id in processed_ids

def mark_processed(post_id, processed_ids):
    processed_ids.add(post_id)

class PersistentDeduper:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_posts (
                    id TEXT PRIMARY KEY
                )
            """)
    def is_duplicate(self, post_id):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT 1 FROM processed_posts WHERE id = ?", (post_id,))
            return cur.fetchone() is not None
    def mark_processed(self, post_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR IGNORE INTO processed_posts (id) VALUES (?)", (post_id,))
