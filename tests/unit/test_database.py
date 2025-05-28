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
