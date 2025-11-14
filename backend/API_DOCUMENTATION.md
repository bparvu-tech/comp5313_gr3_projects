# API Documentation

## API Base URLs

### Development
- Local: `http://localhost:5000`
- Interactive Docs: `http://localhost:5000/docs/`

### Production
- Live API: `https://comp5313lakeheadu.pythonanywhere.com`
- Interactive Docs: `https://comp5313lakeheadu.pythonanywhere.com/docs/`

## Available Endpoints

### Health Check
- **GET** `/api/v1/health/` - Check if the service is running

### Chat with Bot
- **POST** `/api/v1/chat/` - Send messages to the chatbot

## CORS Configuration

The API accepts requests from any origin for development purposes:
```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

This allows frontend applications hosted on any domain to make requests to the API.

## Example Usage

### 1. Check if service is running
```bash
# Local
curl http://localhost:5000/api/v1/health/

# Production
curl https://comp5313lakeheadu.pythonanywhere.com/api/v1/health/
```

### 2. Chat with the bot
```bash
# Local
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what programs does Lakehead offer?"}'

# Production
curl -X POST https://comp5313lakeheadu.pythonanywhere.com/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what programs does Lakehead offer?"}'
```

## Request/Response Format

### Chat Request
```json
{
  "message": "Your question here",
  "session_id": "optional-session-id"
}
```

### Chat Response
```json
{
  "response": "Bot's answer",
  "session_id": "session-id",
  "timestamp": "2025-01-27T20:40:47.080034Z"
}
```

## How It Works

1. **Make API changes** in your code
2. **Restart the server** (`python run.py`)
3. **Documentation updates automatically** - no manual work!

## For Developers

### Adding New Endpoints
1. Add code in `app/api_routes.py`
2. Restart server
3. Documentation appears automatically at `/docs/`

### Key Files
- `app/api_routes.py` - API endpoints and documentation

---

**That's it!** The documentation stays up-to-date automatically. Just use the interactive docs at `/docs/` to explore and test the API.
