"""
REST API endpoints for meeting management.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    JoinMeetingRequest,
    MeetingResponse,
    BriefingResponse,
    AskQuestionRequest,
    QuestionResponse,
    MeetingStatus,
    MeetingPlatform
)
from app.services.recall_service import RecallService
from app.services.openai_service import OpenAIService
from app.services.redis_service import RedisService
from app.config import get_settings
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/meetings", tags=["meetings"])

# Service instances (will be initialized in main.py)
recall_service: RecallService = None
openai_service: OpenAIService = None
redis_service: RedisService = None


def init_services(recall: RecallService, openai: OpenAIService, redis: RedisService):
    """Initialize service instances"""
    global recall_service, openai_service, redis_service
    recall_service = recall
    openai_service = openai
    redis_service = redis


@router.post("/join", response_model=MeetingResponse)
async def join_meeting(request: JoinMeetingRequest):
    """
    Send bot to join a meeting.
    
    Args:
        request: Meeting join request with URL and user ID
        
    Returns:
        Meeting response with bot information
    """
    try:
        settings = get_settings()
        
        # Construct WebSocket URL for receiving transcription
        websocket_url = f"wss://{settings.websocket_domain}/ws/{request.user_id}"
        
        # Create bot via Recall.ai
        bot_data = await recall_service.create_bot(
            meeting_url=str(request.meeting_url),
            websocket_url=websocket_url,
            bot_name=request.bot_name
        )
        
        # Detect platform from URL
        url_str = str(request.meeting_url).lower()
        if "zoom.us" in url_str:
            platform = MeetingPlatform.ZOOM
        elif "teams.microsoft.com" in url_str or "teams.live.com" in url_str:
            platform = MeetingPlatform.TEAMS
        elif "meet.google.com" in url_str:
            platform = MeetingPlatform.MEET
        else:
            platform = MeetingPlatform.UNKNOWN
        
        # Store meeting state in Redis
        meeting_state = {
            "meeting_id": bot_data["id"],
            "user_id": request.user_id,
            "bot_id": bot_data["id"],
            "status": MeetingStatus.PENDING.value,
            "platform": platform.value,
            "bot_name": request.bot_name,
            "transcript": "",
            "speakers": [],
            "started_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        await redis_service.save_meeting_state(bot_data["id"], meeting_state)
        
        logger.info(f"Bot {bot_data['id']} joining meeting for user {request.user_id}")
        
        return MeetingResponse(
            meeting_id=bot_data["id"],
            status=MeetingStatus.PENDING,
            platform=platform,
            joined_at=datetime.utcnow(),
            bot_name=request.bot_name,
            user_id=request.user_id
        )
        
    except Exception as e:
        logger.error(f"Error joining meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/brief", response_model=BriefingResponse)
async def get_brief(meeting_id: str):
    """
    Get current meeting briefing.
    
    Args:
        meeting_id: Unique meeting identifier
        
    Returns:
        Briefing with summary and key points
    """
    try:
        # Get meeting state from Redis
        state = await redis_service.get_meeting_state(meeting_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Get transcript
        transcript = state.get("transcript", "")
        
        if not transcript:
            return BriefingResponse(
                meeting_id=meeting_id,
                brief="Meeting is starting. No discussion yet.",
                key_points=[],
                speakers=[],
                duration_minutes=0,
                last_updated=datetime.utcnow()
            )
        
        # Generate brief using OpenAI
        brief_data = await openai_service.generate_brief(transcript)
        
        # Calculate duration
        started_at = datetime.fromisoformat(state["started_at"])
        duration_minutes = int((datetime.utcnow() - started_at).total_seconds() / 60)
        
        # Get speakers
        speakers = state.get("speakers", [])
        if not speakers:
            speakers = await openai_service.analyze_speakers(transcript)
            await redis_service.update_field(meeting_id, "speakers", speakers)
        
        return BriefingResponse(
            meeting_id=meeting_id,
            brief=brief_data["brief"],
            key_points=brief_data["key_points"],
            speakers=speakers,
            duration_minutes=duration_minutes,
            last_updated=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating brief: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{meeting_id}/ask", response_model=QuestionResponse)
async def ask_question(meeting_id: str, request: AskQuestionRequest):
    """
    Ask bot to speak a question in the meeting.
    
    Args:
        meeting_id: Unique meeting identifier
        request: Question request
        
    Returns:
        Question response with generated text
    """
    try:
        # Get meeting state
        state = await redis_service.get_meeting_state(meeting_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Get recent transcript for context
        transcript = await redis_service.get_transcript(meeting_id, last_n_chars=2000)
        
        # Generate natural response using OpenAI
        response_text = await openai_service.generate_response(
            request.question,
            transcript
        )
        
        # Make bot speak the response
        await recall_service.send_speech(state["bot_id"], response_text)
        
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Bot {state['bot_id']} answering: {response_text}")
        
        return QuestionResponse(
            status="speaking",
            question_id=question_id,
            question_text=request.question,
            response_text=response_text,
            will_speak_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error asking question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/status")
async def get_meeting_status(meeting_id: str):
    """
    Get meeting status.
    
    Args:
        meeting_id: Unique meeting identifier
        
    Returns:
        Meeting state information
    """
    try:
        state = await redis_service.get_meeting_state(meeting_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Get bot status from Recall.ai
        bot_data = await recall_service.get_bot(state["bot_id"])
        
        return {
            "meeting_id": meeting_id,
            "status": state.get("status"),
            "platform": state.get("platform"),
            "bot_status": bot_data.get("status_changes", [])[-1] if bot_data.get("status_changes") else None,
            "duration_minutes": int((datetime.utcnow() - datetime.fromisoformat(state["started_at"])).total_seconds() / 60),
            "has_transcript": bool(state.get("transcript"))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting meeting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{meeting_id}/leave")
async def leave_meeting(meeting_id: str):
    """
    Make bot leave the meeting.
    
    Args:
        meeting_id: Unique meeting identifier
        
    Returns:
        Leave status
    """
    try:
        state = await redis_service.get_meeting_state(meeting_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Make bot leave via Recall.ai
        await recall_service.leave_meeting(state["bot_id"])
        
        # Update state
        await redis_service.update_field(meeting_id, "status", MeetingStatus.ENDED.value)
        
        logger.info(f"Bot {state['bot_id']} left meeting")
        
        return {
            "meeting_id": meeting_id,
            "status": "left",
            "message": "Bot has left the meeting"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))
