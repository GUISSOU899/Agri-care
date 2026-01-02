import os
import redis
import logging
from typing import Optional

# Read Redis URL from environment (set in .env and docker-compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create a Redis client instance (singleton)
_client: Optional[redis.Redis] = None
logger = logging.getLogger(__name__)

def get_redis_client() -> redis.Redis:
    global _client
    if _client is None:
        try:
            _client = redis.from_url(REDIS_URL, decode_responses=True)
            # Test connection immediately
            _client.ping()
            logger.info(f"Successfully connected to Redis at {REDIS_URL}")
        except redis.ConnectionError as e:
            logger.warning(f"Failed to connect to Redis at {REDIS_URL}: {e}")
            # We still return the client so lazy reconnection can happen, 
            # or raising error if strictly required. For now, logging warning.
    return _client

