#!/usr/bin/python3.8
"""
WSGI configuration for PythonAnywhere deployment
"""
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set environment variables for Dialogflow
os.environ.setdefault('DIALOGFLOW_PROJECT_ID', 'lu-assistant-bot')

# Import the Flask application
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
