import sqlite3
import datetime

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
            # Check if the table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_posts'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # Create new table with timestamp column
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS processed_posts (
                        id TEXT PRIMARY KEY,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                # Check if processed_at column exists
                try:
                    conn.execute("SELECT processed_at FROM processed_posts LIMIT 1")
                except sqlite3.OperationalError:
                    # Add the processed_at column to existing table
                    conn.execute("ALTER TABLE processed_posts ADD COLUMN processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    conn.commit()
            
            # Create a table to track batch runs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
            """)
            
    def is_duplicate(self, post_id):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT 1 FROM processed_posts WHERE id = ?", (post_id,))
            return cur.fetchone() is not None
            
    def mark_processed(self, post_id):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_posts (id, processed_at) VALUES (?, ?)", 
                (post_id, current_time)
            )
            
    def record_batch_run(self, status="completed"):
        """Record a batch run with status (started, completed, failed)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO batch_runs (status) VALUES (?)",
                (status,)
            )
            
    def get_stats(self):
        """Get statistics about processed posts and batch runs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get total number of processed posts
            cursor.execute("SELECT COUNT(*) as count FROM processed_posts")
            total_processed = cursor.fetchone()['count']
            
            # Get number of posts processed today
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                "SELECT COUNT(*) as count FROM processed_posts WHERE date(processed_at) = ?", 
                (today,)
            )
            processed_today = cursor.fetchone()['count']
            
            # Get timestamp of the last batch run
            cursor.execute(
                "SELECT run_at FROM batch_runs ORDER BY run_at DESC LIMIT 1"
            )
            last_run_row = cursor.fetchone()
            last_run = last_run_row['run_at'] if last_run_row else None
            
            return {
                'total_processed': total_processed,
                'processed_today': processed_today,
                'last_run': last_run
            }
