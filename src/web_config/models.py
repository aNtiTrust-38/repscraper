from pydantic import BaseModel
from typing import List, Optional

class RedditConfig(BaseModel):
    client_id: str
    client_secret: str
    user_agent: str
    subreddits: List[str]

class TelegramConfig(BaseModel):
    bot_token: str
    chat_id: str
    notification_format: str

class ScrapingConfig(BaseModel):
    batch_interval_hours: int
    max_posts_per_batch: int
    enable_comments: bool
    monitor_new_posts: bool
    monitor_hot_posts: bool

class FiltersConfig(BaseModel):
    min_upvotes: int
    min_comments: int
    max_age_hours: int
    quality_threshold: float
    exclude_deleted: bool
    exclude_removed: bool

class PlatformConfig(BaseModel):
    priority: int
    enabled: bool
    weight: float

class PlatformsConfig(BaseModel):
    taobao: PlatformConfig
    weidian: PlatformConfig
    _1688: PlatformConfig
    yupoo: PlatformConfig
    others: PlatformConfig
    pandabuy: PlatformConfig

class JadeshipConfig(BaseModel):
    enabled: bool
    api_url: str
    timeout_seconds: int
    retry_attempts: int
    default_agent: str
    agent_priority: List[str]

class DatabaseConfig(BaseModel):
    url: str
    backup_enabled: bool
    backup_interval_hours: int
    cleanup_old_data: bool
    retention_days: int

class HealthConfig(BaseModel):
    enabled: bool
    telegram_alerts: bool
    discord_webhook: Optional[str]
    pushbullet_token: Optional[str]
    check_interval_minutes: int

class LoggingConfig(BaseModel):
    level: str
    max_file_size_mb: int
    backup_count: int
    console_output: bool

class ConfigModel(BaseModel):
    reddit: RedditConfig
    telegram: TelegramConfig
    scraping: ScrapingConfig
    filters: FiltersConfig
    platforms: PlatformsConfig
    jadeship: JadeshipConfig
    database: DatabaseConfig
    health: HealthConfig
    logging: LoggingConfig 