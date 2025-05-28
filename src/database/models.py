from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProcessedPost(Base):
    __tablename__ = 'processed_posts'
    id = Column(String, primary_key=True)  # Reddit post ID
    subreddit = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_utc = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=False)
    upvotes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    flair = Column(String)
    content_hash = Column(String)  # For duplicate detection
