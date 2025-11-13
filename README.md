# Lakehead University Chatbot - COMP5313 Group 3 Project

A full-stack chatbot application for Lakehead University, built with Flask, Dialogflow, and modern web technologies.

## 🎯 Project Overview

This chatbot helps students, prospective students, and visitors get information about:

- Academic programs and courses
- Admissions and applications
- Student services and resources
- Campus life and facilities
- Tuition and fees
- Housing and residence

**Status**: ✅ **Prototype Ready for Demonstration**

## 🚀 Quick Start

```bash
# 1. Start Backend
cd backend
pip install -r requirements.txt
python run.py

# 2. Start Frontend (in new terminal)
cd frontend
python3 serve.py

# 3. Open browser
http://localhost:8080
```

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

## 📦 What's Included

### ✅ Backend (Flask + Dialogflow)
- RESTful API with Swagger documentation
- Dialogflow integration for natural language processing
- Session management for conversation context
- Comprehensive error handling and logging
- CORS enabled for frontend integration
- Ready for PythonAnywhere deployment

**Location**: `backend/`  
**Documentation**: [backend/README.md](backend/README.md)

### ✅ Frontend (HTML/CSS/JavaScript)
- Modern, responsive chatbot interface
- Lakehead University branding
- Real-time message handling
- Typing indicators and smooth animations
- Mobile-friendly design
- No build step required

**Location**: `frontend/`  
**Documentation**: [frontend/README.md](frontend/README.md)

### ✅ Training Data (Auto-Generated)
- 78 intents generated from scraped LU website data
- 4 entity types (programs, services, locations, departments)
- Training phrases and responses ready to use

**Location**: `data/dialogflow_ready/`  
**Agent Console**: https://conversational-agents.cloud.google.com/projects/comp5313-chatbot-473118/locations/global/agents

### ✅ Data Collection Scripts
- Web scraper for Lakehead University website
- Intent generator for Dialogflow
- 1,799 markdown files with university information

**Location**: `scripts/`

## 🏗️ Architecture

```
┌─────────────┐       ┌─────────────┐       ┌──────────────────┐
│   Frontend  │ ─────>│   Backend   │ ─────>│ Conversational   │
│  (Browser)  │ <─────│   (Flask)   │ <─────│ Agents (GCP)     │
└─────────────┘       └─────────────┘       └──────────────────┘
   index.html          api_routes.py         comp5313-chatbot
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
│   │       └── dialogflow_service.py
│   ├── run.py                 # Development server
│   ├── wsgi.py                # Production WSGI
│   ├── requirements.txt       # Python dependencies
│   ├── README.md              # Backend documentation
│   ├── API_DOCUMENTATION.md   # API reference
│   └── DEPLOYMENT.md          # PythonAnywhere deployment guide
│
├── frontend/                   # Web interface
│   ├── index.html             # Single-page chatbot app
│   ├── serve.py               # Local development server
│   └── README.md              # Frontend documentation
│
├── data/
│   ├── lakehead_scraped/      # Scraped website data (1,799 files)
│   └── dialogflow_ready/      # Generated Dialogflow intents
│       ├── intents/           # Intent JSON files (78 intents)
│       ├── entities/          # Entity definitions (4 types)
│       ├── intents_bulk_import.json
│       ├── statistics.json
│       └── UPLOAD_INSTRUCTIONS.md
│
├── scripts/
│   ├── scrape_lakehead.py     # Web scraper
│   ├── generate_dialogflow_intents.py  # Intent generator
│   └── README.md              # Scripts documentation
│
├── QUICK_START.md             # Quick start guide
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

## 🧪 Testing

### Test Backend

```bash
# Health check
curl http://localhost:5000/api/v1/health/

# Chat endpoint
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

### Test Frontend

1. Open http://localhost:8080 in browser
2. Open Developer Console (F12)
3. Send test messages
4. Verify responses appear correctly

### API Documentation

- Swagger UI: http://localhost:5000/docs/
- OpenAPI Spec: http://localhost:5000/api/v1/swagger.json

## 🌐 Deployment

### PythonAnywhere (Recommended)

**Backend**:

```bash
1. Upload backend/ folder
2. Install dependencies: pip install -r requirements.txt
3. Configure WSGI file
4. Add dialogflow_key.json
5. Reload web app
```

**Frontend**:

```bash
1. Upload frontend/index.html to static/
2. Configure static files mapping
3. Access at https://username.pythonanywhere.com/
```

**Full Guide**: See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)

### Alternative Platforms

- **Frontend**: GitHub Pages, Netlify, Vercel
- **Backend**: Heroku, Google Cloud Run, AWS Elastic Beanstalk
- **Dialogflow**: Already hosted on Google Cloud

## 🔧 Development Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Dialogflow service account key
- Modern web browser

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
export DIALOGFLOW_PROJECT_ID="lu-assistant-bot"
export DIALOGFLOW_KEY_PATH="dialogflow_key.json"
python run.py
```

### Frontend Setup

```bash
cd frontend
python3 serve.py
# or
python3 -m http.server 8080
```

### Generate Dialogflow Intents

```bash
cd scripts
python3 generate_dialogflow_intents.py
```

## 📊 Project Statistics

- **Backend Lines of Code**: ~700
- **Frontend**: Single HTML file (~12KB)
- **Intents Generated**: 78
- **Entities**: 4 types
- **Source Data**: 1,799 markdown files
- **Data Coverage**: Programs, admissions, services, campus life

## 🔐 Security & Configuration

### Required Files (Not in Git)

- `backend/dialogflow_key.json` - Dialogflow service account credentials

### Environment Variables
```bash
DIALOGFLOW_PROJECT_ID=lu-assistant-bot
DIALOGFLOW_KEY_PATH=/path/to/dialogflow_key.json
```

### Security Notes

- ⚠️ Never commit `dialogflow_key.json`
- ⚠️ Disable CORS wildcard in production
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for production

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[backend/README.md](backend/README.md)** - Backend documentation
- **[backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)** - API reference
- **[backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)** - Deployment guide
- **[frontend/README.md](frontend/README.md)** - Frontend documentation
- **[data/dialogflow_ready/UPLOAD_INSTRUCTIONS.md](data/dialogflow_ready/UPLOAD_INSTRUCTIONS.md)** - Dialogflow setup

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

- Check if Python 3.8+ is installed
- Verify all dependencies are installed
- Ensure `dialogflow_key.json` exists

**Frontend can't connect**:

- Verify backend is running on port 5000
- Check CORS configuration
- Review browser console for errors

**Dialogflow not responding**:

- Verify intents are uploaded
- Check Dialogflow console for agent status
- Review backend logs for API errors

**See**: [QUICK_START.md](QUICK_START.md#troubleshooting) for detailed solutions

## 📞 Support

For issues or questions:

1. Check documentation in respective directories
2. Review error logs (browser console / backend terminal)
3. Verify all services are running
4. Check Dialogflow console

## 📄 License

This project is created for educational purposes as part of COMP5313 coursework at Lakehead University.

## 🎉 Getting Started Now

Ready to see it in action?

```bash
# Clone the repository
git clone https://github.com/bparvu-tech/comp5313_gr3_projects.git
cd comp5313_gr3_projects

# Follow the Quick Start guide
cat QUICK_START.md
```

**Happy Chatting! 🤖**
