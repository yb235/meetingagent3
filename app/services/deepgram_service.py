"""
Deepgram integration service for real-time speech transcription.
"""

from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from typing import Callable, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class DeepgramService:
    """Service for real-time speech transcription using Deepgram"""
    
    def __init__(self, api_key: str):
        """
        Initialize Deepgram service.
        
        Args:
            api_key: Deepgram API key
        """
        self.api_key = api_key
        self.client = DeepgramClient(api_key)
        self.connection = None
    
    async def start_transcription(
        self,
        on_transcript: Callable,
        on_error: Optional[Callable] = None
    ):
        """
        Start live transcription.
        
        Args:
            on_transcript: Callback function for transcript events
            on_error: Optional callback function for error events
            
        Returns:
            Connection object
        """
        try:
            # Create live transcription connection
            self.connection = self.client.listen.live.v("1")
            
            # Configure transcription options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                punctuate=True,
                interim_results=True,
                utterance_end_ms=1000,
                smart_format=True,
                diarize=True  # Speaker diarization
            )
            
            # Set up event handlers
            self.connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
            
            if on_error:
                self.connection.on(LiveTranscriptionEvents.Error, on_error)
            else:
                self.connection.on(
                    LiveTranscriptionEvents.Error,
                    lambda error: logger.error(f"Deepgram error: {error}")
                )
            
            # Start the connection
            if not await self.connection.start(options):
                logger.error("Failed to start Deepgram connection")
                raise Exception("Failed to start Deepgram connection")
            
            logger.info("Deepgram transcription started")
            return self.connection
            
        except Exception as e:
            logger.error(f"Error starting Deepgram transcription: {e}")
            raise
    
    async def send_audio(self, audio_data: bytes):
        """
        Send audio data to Deepgram for transcription.
        
        Args:
            audio_data: Raw audio bytes
        """
        if self.connection:
            try:
                self.connection.send(audio_data)
            except Exception as e:
                logger.error(f"Error sending audio to Deepgram: {e}")
    
    async def stop_transcription(self):
        """Stop the transcription connection"""
        if self.connection:
            try:
                await self.connection.finish()
                logger.info("Deepgram transcription stopped")
            except Exception as e:
                logger.error(f"Error stopping Deepgram transcription: {e}")
