# Performance optimization configurations
import os

class ScalingConfig:
    # Caching configuration
    CACHE_TYPE = "RedisCache" if os.getenv("REDIS_URL") else "SimpleCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Session configuration for multiple instances
    SESSION_TYPE = 'redis' if os.getenv("REDIS_URL") else 'filesystem'
    SESSION_REDIS = os.getenv("REDIS_URL")
    
    # Performance settings - only for PostgreSQL
    # SQLite engine options will be set in Config class
    if os.getenv("DATABASE_URL") and 'postgresql' in os.getenv("DATABASE_URL", ""):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 20,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
    # Note: For SQLite, engine options are set in config.py
