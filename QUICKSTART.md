# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed (for deployment)
- [ ] Recall.ai API key obtained
- [ ] Deepgram API key obtained
- [ ] OpenAI API key obtained (with credits added)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/yb235/meetingagent3.git
cd meetingagent3
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API keys
# Required fields:
# - RECALL_API_KEY
# - DEEPGRAM_API_KEY
# - OPENAI_API_KEY
# - WEBSOCKET_DOMAIN (use localhost:8000 for local testing)
```

### 3. Choose Deployment Method

#### Option A: Local Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Docker Deployment

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 4. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"Meeting Agent API","version":"1.0.0"}

# Access API documentation
# Open browser: http://localhost:8000/docs
```

## Usage Examples

### Join a Meeting

```bash
curl -X POST http://localhost:8000/meetings/join \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://zoom.us/j/123456789",
    "user_id": "your_user_id",
    "bot_name": "AI Assistant"
  }'
```

### Get Meeting Brief

```bash
# Replace {meeting_id} with the ID from join response
curl http://localhost:8000/meetings/{meeting_id}/brief
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/meetings/{meeting_id}/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main discussion points?",
    "wait_for_pause": true
  }'
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app

# Run specific test file
pytest tests/unit/test_schemas.py -v
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the project root directory
cd /path/to/meetingagent3

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Redis Connection Errors

```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker run -d -p 6379:6379 redis:7-alpine
```

### API Key Errors

```bash
# Verify .env file exists
ls -la .env

# Check .env has all required keys
cat .env | grep API_KEY
```

## Next Steps

1. ✅ Set up your environment
2. ✅ Run the application
3. ✅ Test with a real meeting
4. 📱 Build a mobile/web client
5. 🚀 Deploy to production

For detailed documentation, see:
- `README.md` - Full documentation
- `architecture.md` - System architecture
- `implementation plan` - Detailed implementation guide
