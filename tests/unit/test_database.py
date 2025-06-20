def test_processed_post_model():
    """Test ProcessedPost SQLAlchemy model creation"""
    from src.database.models import ProcessedPost
    post = ProcessedPost(
        id='abc123',
        subreddit='FashionReps',
        title='Test Post',
        author='testuser',
        created_utc='2023-01-01T00:00:00',
        processed_at='2023-01-01T02:00:00',
        upvotes=10,
        comments=2,
        quality_score=0.5,
        flair='QC',
        content_hash='hash123'
    )
    assert post.id == 'abc123'

def test_duplicate_prevention():
    from src.database.crud import is_duplicate, mark_processed
    processed_ids = set()
    post_id = 'abc123'
    assert not is_duplicate(post_id, processed_ids)
    mark_processed(post_id, processed_ids)
    assert is_duplicate(post_id, processed_ids)

def test_persistent_duplicate_prevention(tmp_path):
    from src.database.crud import PersistentDeduper
    db_path = tmp_path / "test.db"
    deduper = PersistentDeduper(str(db_path))
    post_id = 'abc123'
    assert not deduper.is_duplicate(post_id)
    deduper.mark_processed(post_id)
    assert deduper.is_duplicate(post_id)
    # Simulate restart
    deduper2 = PersistentDeduper(str(db_path))
    assert deduper2.is_duplicate(post_id)
