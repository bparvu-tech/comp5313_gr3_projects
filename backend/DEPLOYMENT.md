# PythonAnywhere Deployment Guide

This guide covers deploying the Lakehead University Chatbot backend to PythonAnywhere.

## Prerequisites

1. PythonAnywhere account (free tier available)
2. Dialogflow service account key (`dialogflow_key.json`)
3. Access to the `lu-assistant-bot` Google Cloud project

## Deployment Steps

### 1. Upload Code to PythonAnywhere

1. Go to the **Files** tab in your PythonAnywhere dashboard
2. Navigate to `/home/yourusername/` (replace `yourusername` with your actual username)
3. Upload the entire `backend` folder
4. Extract if needed

### 2. Set Up Virtual Environment

1. Go to the **Consoles** tab
2. Open a **Bash console**
3. Navigate to your backend directory:
   ```bash
   cd /home/yourusername/backend
   ```

4. Create a virtual environment:
   ```bash
   python3.8 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Upload Dialogflow Credentials

1. In the **Files** tab, navigate to your backend directory
2. Upload `dialogflow_key.json` to the backend folder
3. Ensure the file is not publicly accessible

### 4. Configure Web App

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Flask**
4. Select Python 3.8
5. Set the source code path to `/home/yourusername/backend`
6. Set the WSGI configuration file path to `/home/yourusername/backend/wsgi.py`

### 5. Update WSGI Configuration

The `wsgi.py` file is already configured, but you may need to update the path if needed.

### 6. Set Environment Variables (Optional)

In the **Web** tab, under **Static files** section, you can add environment variables:
- `DIALOGFLOW_PROJECT_ID=lu-assistant-bot`
- `DIALOGFLOW_KEY_PATH=/home/yourusername/backend/dialogflow_key.json`

### 7. Reload Web App

1. Go to the **Web** tab
2. Click the **Reload** button to restart your web app

## Testing Deployment

### Health Check
```bash
curl https://yourusername.pythonanywhere.com/health
```

Expected response:
```json
{
  "service": "lakehead-chatbot-backend",
  "status": "healthy",
  "version": "prototype-1"
}
```

### Chat Endpoint
```bash
curl -X POST https://yourusername.pythonanywhere.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test-session"}'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed in the virtual environment
2. **Dialogflow Credentials**: Verify `dialogflow_key.json` is in the correct location
3. **CORS Issues**: The app is configured for CORS, but you may need to add your frontend domain
4. **Memory Issues**: Free tier has limited memory; consider upgrading if needed

### Logs

Check the error logs in the **Web** tab for debugging information.

## Security Notes

- Never commit `dialogflow_key.json` to version control
- The file is already listed in `.gitignore`
- Ensure the service account has minimal required permissions

## Performance Optimization

For production deployment:
1. Consider upgrading to a paid PythonAnywhere plan
2. Implement caching for frequent queries
3. Add rate limiting
4. Monitor memory and CPU usage
