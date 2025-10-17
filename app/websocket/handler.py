"""
WebSocket handler for real-time audio and transcription processing.
"""

from fastapi import WebSocket, WebSocketDisconnect
from app.services.deepgram_service import DeepgramService
from app.services.redis_service import RedisService
from app.models.schemas import MeetingStatus
import logging
import json

logger = logging.getLogger(__name__)

# Service instances (will be initialized in main.py)
deepgram_service: DeepgramService = None
redis_service: RedisService = None


def init_services(deepgram: DeepgramService, redis: RedisService):
    """Initialize service instances"""
    global deepgram_service, redis_service
    deepgram_service = deepgram
    redis_service = redis


async def handle_websocket(websocket: WebSocket, user_id: str):
    """
    Handle WebSocket connection for audio/transcription streaming.
    
    Args:
        websocket: WebSocket connection
        user_id: User identifier
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for user {user_id}")
    
    # Find the meeting for this user
    # In a real implementation, you would look this up properly
    # For now, we'll track the meeting_id from the first message
    meeting_id = None
    deepgram_connection = None
    
    try:
        # Set up transcript callback
        async def on_transcript(self, result, **kwargs):
            try:
                nonlocal meeting_id
                
                sentence = result.channel.alternatives[0].transcript
                
                if len(sentence) == 0:
                    return
                
                if result.is_final:
                    logger.info(f"Transcript: {sentence}")
                    
                    # Append to Redis transcript
                    if meeting_id:
                        await redis_service.append_transcript(meeting_id, sentence)
                        
                        # Send transcript update to client
                        await websocket.send_json({
                            "type": "transcript_update",
                            "data": {
                                "text": sentence,
                                "is_final": True,
                                "timestamp": result.start
                            }
                        })
                else:
                    # Send interim results
                    await websocket.send_json({
                        "type": "transcript_update",
                        "data": {
                            "text": sentence,
                            "is_final": False,
                            "timestamp": result.start
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error processing transcript: {e}")
        
        # Start Deepgram transcription
        deepgram_connection = await deepgram_service.start_transcription(
            on_transcript=on_transcript
        )
        
        # Main message loop
        while True:
            # Receive data from client
            data = await websocket.receive()
            
            if "text" in data:
                # Handle text messages (control messages)
                try:
                    message = json.loads(data["text"])
                    message_type = message.get("type")
                    
                    if message_type == "meeting_started":
                        # Client notifies us of the meeting ID
                        meeting_id = message.get("meeting_id")
                        logger.info(f"WebSocket associated with meeting {meeting_id}")
                        
                        # Update meeting status to active
                        await redis_service.update_field(
                            meeting_id,
                            "status",
                            MeetingStatus.ACTIVE.value
                        )
                        
                        await websocket.send_json({
                            "type": "ack",
                            "data": {"message": "Meeting started"}
                        })
                    
                    elif message_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "data": {}
                        })
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {data['text']}")
            
            elif "bytes" in data:
                # Handle binary audio data
                audio_bytes = data["bytes"]
                
                # Forward audio to Deepgram
                if deepgram_connection:
                    await deepgram_service.send_audio(audio_bytes)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    
    finally:
        # Clean up
        if deepgram_connection:
            await deepgram_service.stop_transcription()
        
        # Update meeting status
        if meeting_id:
            try:
                await redis_service.update_field(
                    meeting_id,
                    "status",
                    MeetingStatus.ENDED.value
                )
            except Exception as e:
                logger.error(f"Error updating meeting status on disconnect: {e}")
        
        logger.info(f"WebSocket cleanup completed for user {user_id}")
