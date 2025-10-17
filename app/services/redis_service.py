"""
Redis service for state management and caching.
"""

import redis.asyncio as redis
import json
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisService:
    """Service for managing state in Redis"""
    
    def __init__(self, redis_url: str):
        """
        Initialize Redis service.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establish connection to Redis"""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def save_meeting_state(self, meeting_id: str, state: Dict[str, Any]):
        """
        Save meeting state to Redis.
        
        Args:
            meeting_id: Unique meeting identifier
            state: Meeting state data
        """
        try:
            key = f"meeting:{meeting_id}"
            state["last_activity"] = datetime.utcnow().isoformat()
            await self.client.set(key, json.dumps(state))
            await self.client.expire(key, 86400)  # Expire after 24 hours
            logger.debug(f"Saved state for meeting {meeting_id}")
        except Exception as e:
            logger.error(f"Error saving meeting state: {e}")
            raise
    
    async def get_meeting_state(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve meeting state from Redis.
        
        Args:
            meeting_id: Unique meeting identifier
            
        Returns:
            Meeting state dict or None if not found
        """
        try:
            key = f"meeting:{meeting_id}"
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting meeting state: {e}")
            raise
    
    async def delete_meeting_state(self, meeting_id: str):
        """
        Delete meeting state from Redis.
        
        Args:
            meeting_id: Unique meeting identifier
        """
        try:
            key = f"meeting:{meeting_id}"
            await self.client.delete(key)
            logger.debug(f"Deleted state for meeting {meeting_id}")
        except Exception as e:
            logger.error(f"Error deleting meeting state: {e}")
            raise
    
    async def append_transcript(self, meeting_id: str, text: str):
        """
        Append text to meeting transcript.
        
        Args:
            meeting_id: Unique meeting identifier
            text: Text to append
        """
        try:
            state = await self.get_meeting_state(meeting_id)
            if state:
                current_transcript = state.get("transcript", "")
                state["transcript"] = f"{current_transcript}\n{text}".strip()
                await self.save_meeting_state(meeting_id, state)
        except Exception as e:
            logger.error(f"Error appending transcript: {e}")
            raise
    
    async def get_transcript(self, meeting_id: str, last_n_chars: Optional[int] = None) -> str:
        """
        Get meeting transcript.
        
        Args:
            meeting_id: Unique meeting identifier
            last_n_chars: Optional limit to last N characters
            
        Returns:
            Transcript text
        """
        try:
            state = await self.get_meeting_state(meeting_id)
            if state:
                transcript = state.get("transcript", "")
                if last_n_chars and len(transcript) > last_n_chars:
                    return transcript[-last_n_chars:]
                return transcript
            return ""
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            raise
    
    async def update_field(self, meeting_id: str, field: str, value: Any):
        """
        Update a specific field in meeting state.
        
        Args:
            meeting_id: Unique meeting identifier
            field: Field name to update
            value: New value
        """
        try:
            state = await self.get_meeting_state(meeting_id)
            if state:
                state[field] = value
                await self.save_meeting_state(meeting_id, state)
        except Exception as e:
            logger.error(f"Error updating field {field}: {e}")
            raise
