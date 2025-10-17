Great question! Let me search for existing open-source projects that combine Recall.ai, Deepgram, and OpenAI for meeting agents to inform our architecture.Excellent! I've found extensive real-world implementations and patterns. Now let me search for more architecture examples and consolidated tech stacks:# Consolidated Tech Stack & Architecture for Live Meeting Agent

Based on extensive analysis of open-source projects and existing implementations, here's a comprehensive plan for building a production-ready meeting agent system with ease of maintenance and development:

## 🎯 **Recommended Consolidated Stack**

### **Core Technology Choice: Recall.ai + Deepgram + OpenAI**

This is the **most consolidated and maintainable** stack for your requirements:

| Component | Technology | Why |
|-----------|-----------|-----|
| **Meeting Bot Infrastructure** | **Recall.ai** | Purpose-built for joining Zoom/Teams/Meet; handles all platform-specific complexities |
| **Real-time Transcription** | **Deepgram** | Fast (300ms latency), accurate, cost-effective ($0.0043/min) |
| **AI Brain & Voice** | **OpenAI Realtime API** | Unified solution for understanding, reasoning, and voice generation |
| **Backend** | **Python (FastAPI)** or **Node.js (Express)** | Both well-supported; choose based on team expertise |
| **WebSocket Management** | Built into FastAPI/Express | Native support, no extra dependencies |
| **State/Session Storage** | **Redis** or **PostgreSQL** | Redis for real-time state, Postgres for persistent data |

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│              Live Meeting (Zoom/Teams/Meet)             │
│                                                           │
│  ┌─────────────┐                                         │
│  │ Recall.ai   │ ◄── Joins as participant                │
│  │    Bot      │ ◄── Captures audio & video             │
│  │             │ ◄── Outputs speech via TTS              │
│  └──────┬──────┘                                         │
└─────────┼──────────────────────────────────────────────┘
          │
          │ Audio Stream (WebSocket)
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                   YOUR BACKEND SERVER                    │
│              (Python FastAPI / Node.js)                  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         WebSocket Orchestrator                   │   │
│  │  • Receives audio from Recall.ai                │   │
│  │  • Forwards to Deepgram for transcription       │   │
│  │  • Sends transcripts to OpenAI                  │   │
│  │  • Receives AI responses                        │   │
│  │  • Sends speech commands back to Recall.ai      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         State Management (Redis)                 │   │
│  │  • Current meeting context                      │   │
│  │  • Conversation history                         │   │
│  │  • User questions queue                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         REST API Endpoints                       │   │
│  │  • POST /meetings/join                          │   │
│  │  • GET /meetings/{id}/brief                     │   │
│  │  • POST /meetings/{id}/ask                      │   │
│  │  • GET /meetings/{id}/status                    │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
          │                    │                   │
          │ Transcription      │ AI Processing     │ Bot Control
          ▼                    ▼                   ▼
    ┌──────────┐         ┌──────────┐       ┌──────────┐
    │ Deepgram │         │  OpenAI  │       │Recall.ai │
    │   STT    │         │ Realtime │       │   API    │
    └──────────┘         │   API    │       └──────────┘
                         └──────────┘
                              │
                              │ User Interface
                              ▼
                    ┌──────────────────┐
                    │  Mobile/Web App  │
                    │  • Get briefings │
                    │  • Send questions│
                    └──────────────────┘
```

---

## 📝 **Implementation Plan**

### **Phase 1: Foundation (Week 1)**

#### **1.1 Backend Setup**

**Python (Recommended for AI/ML ecosystem):**
```bash
# Project structure
meeting-agent/
├── app/
│   ├── main.py              # FastAPI application
│   ├── websocket_handler.py # WebSocket connections
│   ├── recall_service.py    # Recall.ai integration
│   ├── deepgram_service.py  # Transcription
│   ├── openai_service.py    # AI processing
│   └── models.py            # Data models
├── requirements.txt
└── docker-compose.yml
```

**Dependencies:**
```txt
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
deepgram-sdk==3.0.0
openai==1.3.0
redis==5.0.1
python-multipart==0.0.6
pydantic==2.5.0
```

#### **1.2 Core Services Implementation**

**Recall.ai Bot Manager:**
```python
# recall_service.py
import requests
from typing import Dict

class RecallService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://us-west-2.recall.ai/api/v1"
    
    def create_bot(self, meeting_url: str, websocket_url: str) -> Dict:
        """Create and send bot to meeting"""
        response = requests.post(
            f"{self.base_url}/bot/",
            headers={"Authorization": f"Token {self.api_key}"},
            json={
                "meeting_url": meeting_url,
                "bot_name": "AI Meeting Assistant",
                "transcription_options": {
                    "provider": "deepgram"
                },
                "real_time_transcription": {
                    "destination_url": websocket_url
                }
            }
        )
        return response.json()
    
    def send_speech(self, bot_id: str, text: str):
        """Make bot speak in meeting"""
        requests.post(
            f"{self.base_url}/bot/{bot_id}/speak",
            headers={"Authorization": f"Token {self.api_key}"},
            json={"text": text}
        )
```

**Deepgram Transcription:**
```python
# deepgram_service.py
from deepgram import DeepgramClient, LiveOptions

class DeepgramService:
    def __init__(self, api_key: str):
        self.client = DeepgramClient(api_key)
    
    async def start_transcription(self, audio_callback):
        """Start live transcription"""
        connection = self.client.listen.live.v("1")
        
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            punctuate=True,
            interim_results=True,
            utterance_end_ms=1000
        )
        
        connection.on("transcript", audio_callback)
        connection.start(options)
        return connection
```

**OpenAI Integration:**
```python
# openai_service.py
from openai import OpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate_brief(self, transcript: str) -> str:
        """Generate meeting briefing"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a meeting assistant. Provide concise briefings."},
                {"role": "user", "content": f"Summarize this meeting discussion: {transcript}"}
            ]
        )
        return response.choices[0].message.content
    
    async def generate_response(self, question: str, context: str) -> str:
        """Generate response to user question"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are in a live meeting. Answer questions based on the discussion."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ]
        )
        return response.choices[0].message.content
```

---

### **Phase 2: Core Features (Week 2)**

#### **REST API Endpoints:**
```python
# main.py
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

app = FastAPI()

class JoinMeetingRequest(BaseModel):
    meeting_url: str
    user_id: str

class AskQuestionRequest(BaseModel):
    question: str

@app.post("/meetings/join")
async def join_meeting(request: JoinMeetingRequest):
    """Send bot to join meeting"""
    websocket_url = f"wss://{YOUR_DOMAIN}/ws/{request.user_id}"
    bot = recall_service.create_bot(request.meeting_url, websocket_url)
    
    # Store meeting state in Redis
    redis.set(f"meeting:{bot['id']}", json.dumps({
        "user_id": request.user_id,
        "bot_id": bot['id'],
        "transcript": ""
    }))
    
    return {"meeting_id": bot['id'], "status": "joining"}

@app.get("/meetings/{meeting_id}/brief")
async def get_brief(meeting_id: str):
    """Get current meeting briefing"""
    meeting_data = json.loads(redis.get(f"meeting:{meeting_id}"))
    transcript = meeting_data["transcript"]
    
    brief = await openai_service.generate_brief(transcript)
    return {"brief": brief, "last_updated": datetime.now()}

@app.post("/meetings/{meeting_id}/ask")
async def ask_question(meeting_id: str, request: AskQuestionRequest):
    """Ask bot to speak a question in the meeting"""
    meeting_data = json.loads(redis.get(f"meeting:{meeting_id}"))
    
    # Generate natural phrasing
    response = await openai_service.generate_response(
        request.question, 
        meeting_data["transcript"]
    )
    
    # Make bot speak
    recall_service.send_speech(meeting_data["bot_id"], response)
    
    return {"status": "question_sent", "text": response}
```

---

### **Phase 3: Real-time Processing (Week 3)**

#### **WebSocket Handler:**
```python
# websocket_handler.py
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    # Initialize Deepgram connection
    deepgram_conn = await deepgram_service.start_transcription(
        lambda transcript: handle_transcript(user_id, transcript)
    )
    
    try:
        while True:
            # Receive audio from Recall.ai
            audio_data = await websocket.receive_bytes()
            
            # Forward to Deepgram
            deepgram_conn.send(audio_data)
    except:
        deepgram_conn.finish()

async def handle_transcript(user_id: str, transcript_data):
    """Process transcribed text"""
    # Update Redis with latest transcript
    # Generate brief every 30 seconds
    # Send to connected clients
    pass
```

---

## 💰 **Cost Analysis**

| Service | Pricing | Typical Meeting (60 min) |
|---------|---------|-------------------------|
| **Recall.ai** | $0.10-0.20/min | $6-12 |
| **Deepgram** | $0.0043/min | $0.26 |
| **OpenAI (GPT-4o-mini)** | $0.15/1M input tokens | ~$1-2 |
| **Total** | | **~$7-15/hour** |

---

## 🔧 **Deployment**

**Docker Compose:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RECALL_API_KEY=${RECALL_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## ✅ **Why This Stack is Best**

1. **Minimal Dependencies**: Only 3 external services (Recall.ai, Deepgram, OpenAI)
2. **Production-Ready**: All services have enterprise-grade reliability
3. **Well-Documented**: Extensive documentation and examples available
4. **Cost-Effective**: Pay-per-use model with transparent pricing
5. **Scalable**: Each component can scale independently
6. **Maintainable**: Clear separation of concerns, standard patterns
7. **Fast Development**: Pre-built solutions for complex problems (meeting joining, transcription, AI)

**Note:** Search results may be incomplete. You can explore more implementations on GitHub: [Recall.ai meeting bot examples](https://github.com/search?q=recall.ai+meeting+bot&type=code), [Deepgram real-time transcription](https://github.com/search?q=deepgram+real-time+transcription&type=code), and [OpenAI realtime API](https://github.com/search?q=openai+realtime+api&type=code).

This architecture provides a **solid, maintainable foundation** that handles all three requirements while being straightforward to develop and deploy.
