"""
Recall.ai integration service for managing meeting bots.
"""

import httpx
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RecallService:
    """Service for interacting with Recall.ai API"""
    
    def __init__(self, api_key: str):
        """
        Initialize Recall.ai service.
        
        Args:
            api_key: Recall.ai API token
        """
        self.api_key = api_key
        self.base_url = "https://us-west-2.recall.ai/api/v1"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_bot(
        self, 
        meeting_url: str, 
        websocket_url: str,
        bot_name: str = "AI Meeting Assistant"
    ) -> Dict:
        """
        Create and send bot to meeting.
        
        Args:
            meeting_url: URL of the meeting to join
            websocket_url: WebSocket endpoint for receiving audio/transcription
            bot_name: Display name for the bot
            
        Returns:
            Dict containing bot information including bot_id
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/bot/",
                    headers=self.headers,
                    json={
                        "meeting_url": meeting_url,
                        "bot_name": bot_name,
                        "transcription_options": {
                            "provider": "deepgram"
                        },
                        "real_time_transcription": {
                            "destination_url": websocket_url
                        }
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                bot_data = response.json()
                logger.info(f"Created bot {bot_data.get('id')} for meeting {meeting_url}")
                return bot_data
            except httpx.HTTPError as e:
                logger.error(f"Failed to create bot: {e}")
                raise
    
    async def get_bot(self, bot_id: str) -> Dict:
        """
        Get bot information.
        
        Args:
            bot_id: ID of the bot
            
        Returns:
            Dict containing bot information
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/bot/{bot_id}/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get bot {bot_id}: {e}")
                raise
    
    async def send_speech(self, bot_id: str, text: str) -> Dict:
        """
        Make bot speak in meeting.
        
        Args:
            bot_id: ID of the bot
            text: Text for the bot to speak
            
        Returns:
            Dict containing speech request status
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/bot/{bot_id}/speak/",
                    headers=self.headers,
                    json={"text": text},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Bot {bot_id} speaking: {text[:50]}...")
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to make bot {bot_id} speak: {e}")
                raise
    
    async def leave_meeting(self, bot_id: str) -> Dict:
        """
        Make bot leave meeting.
        
        Args:
            bot_id: ID of the bot
            
        Returns:
            Dict containing leave request status
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/bot/{bot_id}/leave/",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Bot {bot_id} left meeting")
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to make bot {bot_id} leave: {e}")
                raise
