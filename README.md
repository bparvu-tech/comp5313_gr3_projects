# Lakehead University Chatbot - COMP5313 Group 3 Project

Backend API for Lakehead University chatbot, built with Flask and Google Dialogflow CX.

## 🎯 Project Overview

This is the **backend API service** that powers the Lakehead University chatbot. It provides conversational AI capabilities to help students, prospective students, and visitors get information about:

- Academic programs and courses
- Admissions and applications
- Student services and resources
- Campus life and facilities
- Tuition and fees
- Housing and residence

**Status**: ✅ **Production Deployed & Operational**

**Live API**: `https://comp5313lakeheadu.pythonanywhere.com`

## 🚀 Quick Start

### For Backend Developers

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables (get credentials from team)
# Create .env file or export variables

# 4. Run development server
python run.py

# 5. Test the API
curl http://localhost:5000/api/v1/health/
```

### For Frontend Developers

See the **Frontend Integration Guide** section below for complete integration instructions with code examples.

## 📦 What's Included

### ✅ Backend API (Flask + Dialogflow CX)
- RESTful API with auto-generated Swagger documentation
- Google Dialogflow CX integration for conversational AI
- Session management for maintaining conversation context
- Comprehensive error handling and logging
- CORS enabled for all frontend integrations
- Deployed on PythonAnywhere (production-ready)

**Location**: `backend/`  
**Documentation**: [backend/README.md](backend/README.md)

### ✅ Dialogflow CX Agent
- Powered by Google Cloud Conversational Agents
- Uses Playbooks for generative AI responses
- Regional endpoint: `us-central1`
- Knowledge base populated from scraped LU data

**Agent Console**: https://conversational-agents.cloud.google.com/projects/comp5313-chatbot-473118/locations/us-central1/agents/a02eb0fe-e6a4-4815-8fa7-c832a259326f

### ✅ Data Collection & Processing
- Web scraper for Lakehead University website
- 1,799 markdown files with university information
- Playbook instruction generator

**Location**: `scripts/`, `data/`

## 🏗️ Architecture

```
┌─────────────────┐       ┌─────────────┐       ┌──────────────────┐
│   Frontend      │ ─────>│   Backend   │ ─────>│ Dialogflow CX    │
│   (Your Team)   │ <─────│   (Flask)   │ <─────│    (GCP)         │
└─────────────────┘       └─────────────┘       └──────────────────┘
   React/Vue/etc.          PythonAnywhere         Generative AI
```

## 📋 Repository Structure

```
comp5313_gr3_projects/
│
├── backend/                    # Flask backend API
│   ├── app/
│   │   ├── __init__.py        # Application factory
│   │   ├── api_routes.py      # API endpoints with Swagger
│   │   ├── config.py          # Configuration
│   │   └── services/
│   │       └── dialogflow_service.py  # Dialogflow CX client
│   ├── run.py                 # Development server
│   ├── wsgi.py                # Production WSGI
│   ├── requirements.txt       # Python dependencies
│   ├── README.md              # Backend documentation
│   ├── API_DOCUMENTATION.md   # API reference
│   └── DEPLOYMENT.md          # PythonAnywhere deployment guide
│
├── data/
│   ├── lakehead_scraped/      # Scraped website data (1,799 files)
│   └── dialogflow_ready/      # Processed data for Dialogflow
│
├── scripts/
│   ├── scrape_lakehead.py     # Web scraper
│   ├── scrape_faq.py          # FAQ scraper
│   └── README.md              # Scripts documentation
│
├── .github/
│   └── workflows/
│       ├── deploy.yml         # Deployment automation
│       ├── deploy-staging.yml # Staging deployment
│       └── deploy-production.yml # Production deployment
│
├── FRONTEND_INTEGRATION.md    # Guide for frontend team
└── README.md                  # This file
```

## 🎓 Usage Examples

### Sample Conversations

**Program Information**:
```
User: What engineering programs are available?
Bot: Lakehead University offers several engineering programs including...
```

**Admissions**:
```
User: How do I apply?
Bot: To apply to Lakehead University, you can...
```

**Student Services**:
```
User: Tell me about residence
Bot: Lakehead University offers residence options at both Thunder Bay and Orillia campuses...
```

## 🧪 Testing the API

### Test Health Endpoint

```bash
# Local
curl http://localhost:5000/api/v1/health/

# Production
curl https://comp5313lakeheadu.pythonanywhere.com/api/v1/health/
```

### Test Chat Endpoint

```bash
# Local
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What programs does Lakehead offer?", "session_id": "test_123"}'

# Production
curl -X POST https://comp5313lakeheadu.pythonanywhere.com/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What programs does Lakehead offer?", "session_id": "test_123"}'
```

### Interactive API Documentation

- **Local**: http://localhost:5000/docs/
- **Production**: https://comp5313lakeheadu.pythonanywhere.com/docs/
- **OpenAPI Spec**: http://localhost:5000/api/v1/swagger.json

## 🌐 Deployment

### Current Production Deployment

**Platform**: PythonAnywhere  
**Live API**: `https://comp5313lakeheadu.pythonanywhere.com`  
**Status**: ✅ Operational

### Automated Deployment (GitHub Actions)

The backend automatically deploys via GitHub Actions when you push to specific branches:

- **feat/deployment branch**: Triggers staging deployment
- **main branch**: Triggers production deployment
- **Manual trigger**: Can be triggered manually from Actions tab

See workflows in `.github/workflows/`:
- `deploy.yml` - Main deployment workflow
- `deploy-staging.yml` - Staging environment
- `deploy-production.yml` - Production environment

### Manual Deployment Guide

For detailed manual deployment instructions, see [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)

### Alternative Platforms

- **Backend**: Heroku, Google Cloud Run, AWS Elastic Beanstalk, Railway
- **Dialogflow CX**: Hosted on Google Cloud (already configured)

## 🔧 Development Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Dialogflow CX service account key
- Git

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/bparvu-tech/comp5313_gr3_projects.git
cd comp5313_gr3_projects/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create a .env file in backend/ with:
# DIALOGFLOW_PROJECT_ID=comp5313-chatbot-473118
# DIALOGFLOW_LOCATION=us-central1
# DIALOGFLOW_AGENT_ID=a02eb0fe-e6a4-4815-8fa7-c832a259326f

# 4. Add service account key
# Place dialogflow_key.json in backend/

# 5. Run development server
python run.py
```

### Verify Installation

```bash
# Test health endpoint
curl http://localhost:5000/api/v1/health/

# Visit interactive docs
open http://localhost:5000/docs/
```

## 🔗 Frontend Integration Guide

This section is for frontend developers who need to integrate with the Lakehead University Chatbot API.

### API Information

#### Production API
- **Base URL**: `https://comp5313lakeheadu.pythonanywhere.com`
- **API Documentation**: `https://comp5313lakeheadu.pythonanywhere.com/docs/`
- **Status**: Live and operational

#### Development API (Local Testing)
- **Base URL**: `http://localhost:5000`
- **API Documentation**: `http://localhost:5000/docs/`

### API Endpoints

#### 1. Health Check
Check if the backend service is running.

**Endpoint**: `GET /api/v1/health/`

**Example Request**:
```javascript
fetch('https://comp5313lakeheadu.pythonanywhere.com/api/v1/health/')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T20:16:08.040Z",
  "service": "Lakehead University Chatbot API"
}
```

#### 2. Chat with Bot
Send a message to the chatbot and receive a response.

**Endpoint**: `POST /api/v1/chat/`

**Request Body**:
```json
{
  "message": "What programs does Lakehead offer?",
  "session_id": "optional-session-id"
}
```

**Parameters**:
- `message` (string, required): The user's message/question
- `session_id` (string, optional): Session identifier to maintain conversation context. If not provided, a new session will be created.

**Example Request**:
```javascript
fetch('https://comp5313lakeheadu.pythonanywhere.com/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What programs does Lakehead offer?',
    session_id: 'user_123_session'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

**Response**:
```json
{
  "response": "Lakehead University offers a wide range of academic programs...",
  "session_id": "user_123_session",
  "timestamp": "2025-11-13T20:16:09.008Z"
}
```

### Complete Integration Examples

#### HTML + Vanilla JavaScript

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LU Chatbot</title>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="user-input" placeholder="Ask me about Lakehead University...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        const API_URL = 'https://comp5313lakeheadu.pythonanywhere.com';
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7);

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();

            if (!message) return;

            // Display user message
            addMessage('user', message);
            input.value = '';

            try {
                // Call API
                const response = await fetch(`${API_URL}/api/v1/chat/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });

                const data = await response.json();

                // Display bot response
                addMessage('bot', data.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            }
        }

        function addMessage(sender, text) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = sender;
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Allow Enter key to send message
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

#### React Example

```javascript
import React, { useState } from 'react';

const API_URL = 'https://comp5313lakeheadu.pythonanywhere.com';
const SESSION_ID = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7);

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: input,
          session_id: SESSION_ID
        })
      });

      const data = await response.json();
      const botMessage = { sender: 'bot', text: data.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="bot">Typing...</div>}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me about Lakehead University..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
```

#### Vue.js Example

```vue
<template>
  <div class="chatbot">
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index" :class="msg.sender">
        {{ msg.text }}
      </div>
      <div v-if="loading" class="bot">Typing...</div>
    </div>
    <div class="input-container">
      <input
        v-model="input"
        @keypress.enter="sendMessage"
        placeholder="Ask me about Lakehead University..."
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      input: '',
      loading: false,
      apiUrl: 'https://comp5313lakeheadu.pythonanywhere.com',
      sessionId: 'session_' + Date.now() + '_' + Math.random().toString(36).substring(7)
    };
  },
  methods: {
    async sendMessage() {
      if (!this.input.trim()) return;

      this.messages.push({ sender: 'user', text: this.input });
      const message = this.input;
      this.input = '';
      this.loading = true;

      try {
        const response = await fetch(`${this.apiUrl}/api/v1/chat/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: message,
            session_id: this.sessionId
          })
        });

        const data = await response.json();
        this.messages.push({ sender: 'bot', text: data.response });
      } catch (error) {
        console.error('Error:', error);
        this.messages.push({
          sender: 'bot',
          text: 'Sorry, I encountered an error. Please try again.'
        });
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

### CORS Support

The backend API has CORS enabled for all origins, so you can call it from any frontend application without CORS issues.

### Session Management

- Each conversation should have a unique `session_id`
- Generate a session ID when the user starts chatting: `'session_' + Date.now() + '_' + Math.random().toString(36).substring(7)`
- Reuse the same `session_id` for all messages in a conversation to maintain context
- If you don't provide a `session_id`, the backend will generate one for you

### Error Handling Best Practices

Always handle potential errors:

```javascript
try {
  const response = await fetch(API_URL + '/api/v1/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMessage, session_id: sessionId })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  // Handle success
} catch (error) {
  console.error('API Error:', error);
  // Display error message to user
}
```

### Testing Your Integration

#### Test with cURL
```bash
curl -X POST https://comp5313lakeheadu.pythonanywhere.com/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What programs does Lakehead offer?"}'
```

#### Test with Browser Console
```javascript
fetch('https://comp5313lakeheadu.pythonanywhere.com/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What programs does Lakehead offer?',
    session_id: 'test_session'
  })
})
  .then(r => r.json())
  .then(d => console.log(d));
```

#### Use Interactive API Documentation
Visit `https://comp5313lakeheadu.pythonanywhere.com/docs/` to test the API interactively.

### Running Backend Locally (Optional)

If you need to test with a local backend:

```bash
# Clone the repository
git clone https://github.com/bparvu-tech/comp5313_gr3_projects.git
cd comp5313_gr3_projects/backend

# Install dependencies
pip install -r requirements.txt

# Set up environment (contact backend team for credentials)
# Create a .env file with:
# DIALOGFLOW_PROJECT_ID=comp5313-chatbot-473118
# DIALOGFLOW_LOCATION=us-central1
# DIALOGFLOW_AGENT_ID=a02eb0fe-e6a4-4815-8fa7-c832a259326f

# Run the server
python run.py
```

The local backend will be available at `http://localhost:5000`

### Sample Questions to Test

- "What programs does Lakehead offer?"
- "How do I apply?"
- "Tell me about residence"
- "What are the tuition fees?"

### Production Checklist

Before going live with your frontend:

- [ ] Replace all localhost URLs with production URL
- [ ] Implement proper error handling
- [ ] Add loading states for better UX
- [ ] Test session management
- [ ] Implement input validation
- [ ] Add rate limiting (if needed)
- [ ] Test on multiple devices/browsers
- [ ] Implement analytics tracking (optional)

## 📊 Project Statistics

- **Backend Lines of Code**: ~700+
- **API Endpoints**: 2 (health, chat)
- **Dialogflow CX Agent**: Playbook-based conversational AI
- **Source Data**: 1,799 markdown files from LU website
- **Data Coverage**: Programs, admissions, services, campus life, residence, fees
- **Deployment**: PythonAnywhere (production), GitHub Actions (CI/CD)

## 🔐 Security & Configuration

### Required Files (Not in Git)

- `backend/dialogflow_key.json` - Dialogflow CX service account credentials
- `backend/.env` - Environment variables (use `env.example` as template)

### Environment Variables
```bash
DIALOGFLOW_PROJECT_ID=comp5313-chatbot-473118
DIALOGFLOW_LOCATION=us-central1
DIALOGFLOW_AGENT_ID=a02eb0fe-e6a4-4815-8fa7-c832a259326f
```

### Security Notes

- ✅ Service account key is in `.gitignore`
- ✅ `.env` files are excluded from version control
- ✅ HTTPS enabled in production (PythonAnywhere)
- ⚠️ CORS is set to `*` for development (consider restricting in production)
- ⚠️ Consider implementing rate limiting for production use

## 📚 Documentation

### For Backend Developers
- **[backend/README.md](backend/README.md)** - Backend overview
- **[backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)** - API reference
- **[backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)** - Deployment guide

### For Frontend Developers
- **Frontend Integration Guide** - See section above with complete code examples

### Additional Resources
- **[scripts/README.md](scripts/README.md)** - Data scraping and processing
- **Interactive API Docs**: https://comp5313lakeheadu.pythonanywhere.com/docs/

## 🤝 Team

**COMP5313 Group 3** - MSc Computer Science Program, Lakehead University

## 🎯 Future Enhancements

### Phase 2 Ideas

- [ ] Voice input/output support
- [ ] Rich media responses (images, videos)
- [ ] Multi-language support (French)
- [ ] Chat history persistence
- [ ] User feedback mechanism
- [ ] Analytics dashboard
- [ ] Admin panel for intent management
- [ ] Integration with LU systems (Student Portal, MyCourseLink)
- [ ] Mobile app (React Native)
- [ ] Proactive notifications

### Technical Improvements

- [ ] Add caching layer (Redis)
- [ ] Implement rate limiting
- [ ] Add comprehensive test suite
- [ ] Set up CI/CD pipeline
- [ ] Implement logging aggregation
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Performance optimization
- [ ] Security hardening

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**:
- Check if Python 3.8+ is installed: `python --version`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure `dialogflow_key.json` exists in `backend/`
- Check `.env` file has correct values

**API returns 403 Permission Denied**:
- Verify service account key is for correct project (comp5313-chatbot-473118)
- Check service account has "Dialogflow API Client" role
- Verify `DIALOGFLOW_PROJECT_ID`, `DIALOGFLOW_LOCATION`, and `DIALOGFLOW_AGENT_ID` are correct

**Dialogflow returns empty responses**:
- Agent needs knowledge: Add content to Playbooks in Dialogflow CX console
- Check agent is published/deployed
- Review Dialogflow CX console logs

**PythonAnywhere deployment issues**:
- Ensure virtualenv is created and activated
- Install all dependencies in the virtualenv
- Check WSGI configuration points to correct app
- Verify environment variables are set
- Reload web app after changes

See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for detailed deployment troubleshooting

## 📞 Support

For issues or questions:

1. **API Documentation**: https://comp5313lakeheadu.pythonanywhere.com/docs/
2. **Backend Docs**: [backend/README.md](backend/README.md)
3. **Frontend Integration**: See Frontend Integration Guide section above
4. **Review error logs**: Check backend terminal or PythonAnywhere logs
5. **Dialogflow Console**: https://conversational-agents.cloud.google.com/

## 📄 License

This project is created for educational purposes as part of COMP5313 coursework at Lakehead University.

## 🎉 Quick Links

### For Backend Team
- **Live API**: https://comp5313lakeheadu.pythonanywhere.com
- **API Docs**: https://comp5313lakeheadu.pythonanywhere.com/docs/
- **Dialogflow Console**: https://conversational-agents.cloud.google.com/projects/comp5313-chatbot-473118/

### For Frontend Team
- **Integration Guide**: See Frontend Integration Guide section above
- **API Base URL**: `https://comp5313lakeheadu.pythonanywhere.com`
- **API Endpoints**: `/api/v1/health/` and `/api/v1/chat/`

### Repository
```bash
git clone https://github.com/bparvu-tech/comp5313_gr3_projects.git
cd comp5313_gr3_projects/backend
```
