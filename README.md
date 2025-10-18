# Meeting Agent API

An AI-powered meeting agent that can join live meetings (Zoom, Microsoft Teams, Google Meet), provide real-time briefings, and answer questions by speaking in the meeting.

## Features

- 🤖 **Join Meetings**: Bot automatically joins Zoom, Teams, or Google Meet
- 📝 **Real-time Transcription**: Live speech-to-text using Deepgram
- 💡 **Smart Briefings**: AI-generated summaries of meeting discussions
- 🗣️ **Interactive Q&A**: Ask questions and bot responds by speaking in the meeting
- ⚡ **Real-time Updates**: WebSocket support for live transcript updates

## Architecture

- **Backend**: Python with FastAPI
- **Meeting Bot**: Recall.ai
- **Transcription**: Deepgram
- **AI Processing**: OpenAI GPT-4o-mini
- **State Management**: Redis
- **Deployment**: Docker

## Prerequisites

### Required API Keys

1. **Recall.ai API Key**
   - Sign up at [https://www.recall.ai/](https://www.recall.ai/)
   - Get API key from Dashboard → Settings → API Keys

2. **Deepgram API Key**
   - Sign up at [https://deepgram.com/](https://deepgram.com/)
   - Get API key from Console → API Keys

3. **OpenAI API Key**
   - Sign up at [https://platform.openai.com/](https://platform.openai.com/)
   - Get API key from API Keys page
   - Add credits to your account (minimum $5)

### Software Requirements

- Python 3.11+
- Docker and Docker Compose (for deployment)
- Redis (or use Docker Compose)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yb235/meetingagent3.git
cd meetingagent3
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```
RECALL_API_KEY=your_recall_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
WEBSOCKET_DOMAIN=your-domain.com  # or localhost:8000 for local testing
```

### 3. Install Dependencies

#### Using Virtual Environment (Development)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Using Docker (Production)

```bash
# Build and start services
docker-compose up --build -d

# Check logs
docker-compose logs -f api
```

### 4. Run the Application

#### Development Mode

```bash
# Make sure virtual environment is activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode (Docker)

```bash
docker-compose up -d
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000

## API Endpoints

### Join a Meeting

```bash
POST /meetings/join
```

Request:
```json
{
  "meeting_url": "https://zoom.us/j/123456789",
  "user_id": "user123",
  "bot_name": "AI Assistant"
}
```

Response:
```json
{
  "meeting_id": "bot_abc123",
  "status": "pending",
  "platform": "zoom",
  "joined_at": "2025-10-17T21:00:00Z",
  "bot_name": "AI Assistant",
  "user_id": "user123"
}
```

### Get Meeting Briefing

```bash
GET /meetings/{meeting_id}/brief
```

Response:
```json
{
  "meeting_id": "bot_abc123",
  "brief": "The meeting is discussing Q4 goals and budget allocation...",
  "key_points": [
    "Budget approval for Q4",
    "Timeline for new project",
    "Team assignments"
  ],
  "speakers": ["John", "Mary", "Bob"],
  "duration_minutes": 25,
  "last_updated": "2025-10-17T21:25:00Z"
}
```

### Ask a Question

```bash
POST /meetings/{meeting_id}/ask
```

Request:
```json
{
  "question": "What are the main discussion points?",
  "wait_for_pause": true
}
```

Response:
```json
{
  "status": "speaking",
  "question_id": "q_abc123",
  "question_text": "What are the main discussion points?",
  "response_text": "Based on our discussion, the main points are budget approval and timeline planning.",
  "will_speak_at": "2025-10-17T21:26:00Z"
}
```

### Get Meeting Status

```bash
GET /meetings/{meeting_id}/status
```

### Leave Meeting

```bash
POST /meetings/{meeting_id}/leave
```

## WebSocket Connection

Connect to real-time transcription updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onopen = () => {
  // Send meeting ID
  ws.send(JSON.stringify({
    type: 'meeting_started',
    meeting_id: 'bot_abc123'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcript_update') {
    console.log('Transcript:', data.data.text);
  }
};
```

## Testing

### Manual Testing

```bash
# Test configuration
python app/config.py

# Test schemas
python app/models/schemas.py

# Run the application
python app/main.py
```

### Using the API

```bash
# Health check
curl http://localhost:8000/health

# Join a test meeting (replace with real meeting URL)
curl -X POST http://localhost:8000/meetings/join \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://zoom.us/j/123456789",
    "user_id": "test_user",
    "bot_name": "Test Bot"
  }'
```

## Project Structure

```
meetingagent3/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── services/
│   │   ├── recall_service.py   # Recall.ai integration
│   │   ├── deepgram_service.py # Transcription service
│   │   ├── openai_service.py   # AI processing
│   │   └── redis_service.py    # State management
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── api/
│   │   └── meetings.py         # REST endpoints
│   └── websocket/
│       └── handler.py          # WebSocket handler
├── tests/
├── docs/
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker configuration
├── Dockerfile                 # Container definition
└── README.md                  # This file
```

## Deployment

### Docker Deployment

1. Set environment variables in `.env`
2. Build and run:
   ```bash
   docker-compose up -d
   ```

### Cloud Deployment (AWS/GCP/Azure)

1. Deploy using container service (ECS, Cloud Run, etc.)
2. Set up Redis (ElastiCache, Cloud Memorystore, etc.)
3. Configure environment variables
4. Set up domain and SSL certificate
5. Update `WEBSOCKET_DOMAIN` in environment

## Cost Estimation

For a 60-minute meeting:

- **Recall.ai**: $6-12
- **Deepgram**: $0.26
- **OpenAI**: $1-2
- **Total**: ~$7-15 per meeting hour

## Troubleshooting

### Bot Not Joining Meeting

- Check Recall.ai API key is valid
- Verify meeting URL is correct and accessible
- Check Recall.ai dashboard for bot status

### No Transcription

- Verify Deepgram API key is valid
- Check WebSocket connection is established
- Check Deepgram credits/balance

### AI Not Responding

- Verify OpenAI API key is valid
- Check OpenAI account has credits
- Review API logs for errors

### Redis Connection Issues

- Verify Redis is running: `docker-compose ps`
- Check Redis connection settings in `.env`
- Test Redis connection: `redis-cli ping`

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Install black
pip install black

# Format code
black app/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yb235/meetingagent3/issues
- Documentation: See `architecture.md` and `implementation plan`

## Acknowledgments

- [Recall.ai](https://www.recall.ai/) - Meeting bot infrastructure
- [Deepgram](https://deepgram.com/) - Speech transcription
- [OpenAI](https://openai.com/) - AI processing
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
