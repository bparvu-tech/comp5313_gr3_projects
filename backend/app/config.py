"""Configuration settings for the Lakehead University Chatbot backend."""
import os

# Base directory = backend/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Path to Dialogflow key (defaults to backend/dialogflow_key.json)
DIALOGFLOW_KEY_PATH = os.getenv(
    "DIALOGFLOW_KEY_PATH",
    os.path.join(BASE_DIR, "dialogflow_key.json")
)

# Project ID
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID", "lu-assistant-bot")

# Optional check: warn if file is missing
if not os.path.exists(DIALOGFLOW_KEY_PATH):
    raise FileNotFoundError(f"Dialogflow credentials file not found: {DIALOGFLOW_KEY_PATH}")
