"""
Data models and schemas for the meeting agent API.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS (Predefined Choices)
# ============================================================================

class MeetingStatus(str, Enum):
    """Possible states of a meeting"""
    PENDING = "pending"
    ACTIVE = "active"
    ENDED = "ended"
    ERROR = "error"


class MeetingPlatform(str, Enum):
    """Meeting platforms we support"""
    ZOOM = "zoom"
    TEAMS = "microsoft_teams"
    MEET = "google_meet"
    UNKNOWN = "unknown"


# ============================================================================
# REQUEST SCHEMAS (Data sent TO the API)
# ============================================================================

class JoinMeetingRequest(BaseModel):
    """Schema for POST /meetings/join"""
    meeting_url: HttpUrl = Field(
        ...,
        description="Full URL of the meeting to join",
        examples=["https://zoom.us/j/123456789?pwd=abc123"]
    )
    user_id: str = Field(
        ...,
        description="Unique identifier for the user",
        examples=["user_abc123"]
    )
    bot_name: Optional[str] = Field(
        default="AI Meeting Assistant",
        description="Name displayed for the bot in the meeting",
        max_length=50
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "meeting_url": "https://zoom.us/j/123456789",
                "user_id": "user_abc123",
                "bot_name": "AI Assistant"
            }
        }


class AskQuestionRequest(BaseModel):
    """Schema for POST /meetings/{meeting_id}/ask"""
    question: str = Field(
        ...,
        description="Question to ask in the meeting",
        min_length=5,
        max_length=500,
        examples=["What are the main discussion points?"]
    )
    wait_for_pause: bool = Field(
        default=True,
        description="Wait for speaking pause before asking"
    )


# ============================================================================
# RESPONSE SCHEMAS (Data returned FROM the API)
# ============================================================================

class MeetingResponse(BaseModel):
    """Schema for meeting information returned by API"""
    meeting_id: str = Field(description="Unique meeting identifier")
    status: MeetingStatus = Field(description="Current meeting status")
    platform: MeetingPlatform = Field(description="Meeting platform detected")
    joined_at: Optional[datetime] = Field(description="When bot joined meeting")
    bot_name: str = Field(description="Bot display name")
    user_id: str = Field(description="Associated user ID")


class TranscriptSegment(BaseModel):
    """A single piece of transcribed speech"""
    speaker: str = Field(description="Speaker identifier")
    text: str = Field(description="Transcribed text")
    timestamp: datetime = Field(description="When this was spoken")
    confidence: float = Field(
        description="Transcription confidence (0-1)",
        ge=0.0,
        le=1.0
    )


class BriefingResponse(BaseModel):
    """Schema for GET /meetings/{meeting_id}/brief"""
    meeting_id: str
    brief: str = Field(description="AI-generated summary")
    key_points: List[str] = Field(
        default=[],
        description="Main discussion points"
    )
    speakers: List[str] = Field(
        default=[],
        description="People who have spoken"
    )
    duration_minutes: int = Field(description="Meeting duration so far")
    last_updated: datetime = Field(description="When brief was generated")
    recent_transcript: Optional[List[TranscriptSegment]] = Field(
        default=[],
        description="Last 5 minutes of conversation"
    )


class QuestionResponse(BaseModel):
    """Schema for POST /meetings/{meeting_id}/ask response"""
    status: str = Field(description="queued, speaking, or completed")
    question_id: str = Field(description="Unique question identifier")
    question_text: str = Field(description="Original question")
    response_text: str = Field(description="AI-generated response")
    will_speak_at: Optional[datetime] = Field(
        description="Estimated time bot will speak"
    )


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(description="Detailed error information")
    code: str = Field(description="Error code for debugging")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# INTERNAL DATA STRUCTURES
# ============================================================================

class MeetingState(BaseModel):
    """Internal state stored in Redis"""
    meeting_id: str
    user_id: str
    bot_id: str
    status: MeetingStatus
    platform: MeetingPlatform
    transcript: str = ""
    speakers: List[str] = []
    started_at: datetime
    last_activity: datetime
    metadata: Dict = {}


# ============================================================================
# WEBSOCKET MESSAGES
# ============================================================================

class WebSocketMessage(BaseModel):
    """Base structure for WebSocket messages"""
    type: str = Field(description="Message type")
    data: Dict = Field(description="Message payload")


if __name__ == "__main__":
    """Test schemas"""
    join_request = JoinMeetingRequest(
        meeting_url="https://zoom.us/j/123456789",
        user_id="user_test",
        bot_name="Test Bot"
    )
    print("Join Request:", join_request.model_dump_json(indent=2))
    
    briefing = BriefingResponse(
        meeting_id="meeting_123",
        brief="Test meeting about Q4 goals",
        key_points=["Goal 1", "Goal 2"],
        speakers=["John", "Mary"],
        duration_minutes=15,
        last_updated=datetime.utcnow()
    )
    print("\nBriefing Response:", briefing.model_dump_json(indent=2))
