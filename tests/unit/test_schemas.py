"""
Unit tests for data models and schemas.
"""

import pytest
from datetime import datetime
from app.models.schemas import (
    JoinMeetingRequest,
    AskQuestionRequest,
    MeetingResponse,
    BriefingResponse,
    MeetingStatus,
    MeetingPlatform,
    TranscriptSegment
)


def test_join_meeting_request():
    """Test JoinMeetingRequest model validation"""
    request = JoinMeetingRequest(
        meeting_url="https://zoom.us/j/123456789",
        user_id="test_user",
        bot_name="Test Bot"
    )
    
    assert "zoom.us/j/123456789" in str(request.meeting_url)
    assert request.user_id == "test_user"
    assert request.bot_name == "Test Bot"


def test_join_meeting_request_default_bot_name():
    """Test default bot name"""
    request = JoinMeetingRequest(
        meeting_url="https://zoom.us/j/123456789",
        user_id="test_user"
    )
    
    assert request.bot_name == "AI Meeting Assistant"


def test_ask_question_request():
    """Test AskQuestionRequest model validation"""
    request = AskQuestionRequest(
        question="What are the main points?",
        wait_for_pause=True
    )
    
    assert request.question == "What are the main points?"
    assert request.wait_for_pause is True


def test_ask_question_request_min_length():
    """Test question minimum length validation"""
    with pytest.raises(ValueError):
        AskQuestionRequest(question="Hi")  # Too short


def test_meeting_response():
    """Test MeetingResponse model"""
    response = MeetingResponse(
        meeting_id="bot_123",
        status=MeetingStatus.ACTIVE,
        platform=MeetingPlatform.ZOOM,
        joined_at=datetime.utcnow(),
        bot_name="Test Bot",
        user_id="user_123"
    )
    
    assert response.meeting_id == "bot_123"
    assert response.status == MeetingStatus.ACTIVE
    assert response.platform == MeetingPlatform.ZOOM


def test_briefing_response():
    """Test BriefingResponse model"""
    briefing = BriefingResponse(
        meeting_id="meeting_123",
        brief="Test briefing",
        key_points=["Point 1", "Point 2"],
        speakers=["Speaker 1", "Speaker 2"],
        duration_minutes=30,
        last_updated=datetime.utcnow()
    )
    
    assert briefing.meeting_id == "meeting_123"
    assert briefing.brief == "Test briefing"
    assert len(briefing.key_points) == 2
    assert len(briefing.speakers) == 2
    assert briefing.duration_minutes == 30


def test_transcript_segment():
    """Test TranscriptSegment model"""
    segment = TranscriptSegment(
        speaker="Speaker 1",
        text="Hello everyone",
        timestamp=datetime.utcnow(),
        confidence=0.95
    )
    
    assert segment.speaker == "Speaker 1"
    assert segment.text == "Hello everyone"
    assert 0.0 <= segment.confidence <= 1.0


def test_transcript_segment_confidence_validation():
    """Test confidence must be between 0 and 1"""
    with pytest.raises(ValueError):
        TranscriptSegment(
            speaker="Speaker 1",
            text="Hello",
            timestamp=datetime.utcnow(),
            confidence=1.5  # Invalid: > 1
        )


def test_meeting_status_enum():
    """Test MeetingStatus enum values"""
    assert MeetingStatus.PENDING.value == "pending"
    assert MeetingStatus.ACTIVE.value == "active"
    assert MeetingStatus.ENDED.value == "ended"
    assert MeetingStatus.ERROR.value == "error"


def test_meeting_platform_enum():
    """Test MeetingPlatform enum values"""
    assert MeetingPlatform.ZOOM.value == "zoom"
    assert MeetingPlatform.TEAMS.value == "microsoft_teams"
    assert MeetingPlatform.MEET.value == "google_meet"
    assert MeetingPlatform.UNKNOWN.value == "unknown"
