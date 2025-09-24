# Lakehead University Chatbot Backend

This backend is part of the **COMP5313 Group 3 Project** - a chatbot for Lakehead University.  
We use [Anaconda](https://www.anaconda.com) for environment management to ensure all team members can run the project in the same setup.

## Features (Prototype 1)

✅ **Core Functionality**
- Flask REST API with Dialogflow integration
- Chat endpoint for user interactions
- Health check endpoint for monitoring
- Session management support

✅ **Production Ready**
- Comprehensive error handling and logging
- Input validation and sanitization
- CORS support for frontend integration
- PythonAnywhere deployment ready

✅ **Security & Monitoring**
- Proper credential management
- Request/response logging
- Error tracking and fallback responses

## 1. Navigate to the backend/ folder

```bash
cd comp5313_gr3_projects/backend
```

## 2. Create and activate the Conda Environment

Make sure you have [Anaconda](https://docs.anaconda.com/anaconda/install/) installed.

Create the environment from the provided `environment.yml` file:

```bash
conda env create -f environment.yml
```

Run:

```bash
conda activate comp5313
```

## 3. Dialogflow Credentials

The backend requires a **Dialogflow service account key** to connect to our bot.

### Option A: If you have GCP access

1. Go to [Google Cloud Console](https://console.cloud.google.com/).  
2. Select the project: **`lu-assistant-bot`**.  
3. Navigate: **IAM & Admin → Service Accounts**.  
4. Open the service account:  

   ```text
   dialogflow-access@lu-assistant-bot.iam.gserviceaccount.com
   ```

5. Go to the **Keys** tab → **Add Key** → **Create new key** → **JSON**.  
6. Download the key file and rename it to:

   ```text
   dialogflow_key.json
   ```

7. Place it in the `backend/` directory.

### Option B: If you cannot access GCP

The project owner will securely provide you with a pre-generated `dialogflow_key.json`.  
Place it in the `backend/` folder.  

⚠️ **dialogflow_key.json** is secret. **Never commit it to GitHub.** It is already listed in `.gitignore`.

## 5. Run the Backend

Make sure you are inside the `backend/` folder and then run:

```bash
python run.py
```

## 6. Updating Dependencies

If new libraries are added during development, update your local environment with:

```bash
conda env update -f environment.yml --prune
```

If you installed new packages, **remember to update the environment file**:

```bash
conda env export > environment.yml
```

## 🚀 API Documentation

### 🌐 Interactive Documentation (Recommended)
- **Swagger UI**: http://localhost:5000/docs/
  - Interactive API explorer
  - Try endpoints directly in browser
  - Always up-to-date with code changes

### 📋 Quick Reference

#### Versioned API (Recommended)
- `GET /api/v1/health/` - Service health check
- `POST /api/v1/chat/` - Chat with the bot

#### Legacy API (Backward Compatible)
- `GET /health` - Legacy health check
- `POST /chat` - Legacy chat endpoint

### 📚 Detailed Documentation
- **Full API Guide**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **OpenAPI Spec**: http://localhost:5000/api/v1/swagger.json

### 🔧 Key Features
- ✅ **Automatic Documentation**: Generated from code, always current
- ✅ **Interactive Testing**: Try endpoints directly in browser
- ✅ **Request Validation**: Automatic input validation
- ✅ **Type Safety**: Guaranteed response formats
- ✅ **Error Handling**: Comprehensive error responses

## Deployment

For PythonAnywhere deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Development Workflow

- All backend code lives under `backend/`.  
- Commit changes through feature branches and submit pull requests for review.  
- Update `environment.yml` if new dependencies are added.
- Test endpoints using the provided curl examples or Postman.
