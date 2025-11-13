"""Configuration settings for the Lakehead University Chatbot backend."""
import os

# Base directory = backend/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Path to Dialogflow key (defaults to backend/dialogflow_key.json)
DIALOGFLOW_KEY_PATH = os.getenv(
    "DIALOGFLOW_KEY_PATH",
    os.path.join(BASE_DIR, "dialogflow_key.json")
)

# Project ID for Dialogflow CX (Conversational Agents)
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID", "comp5313-chatbot-473118")

# Dialogflow CX Agent settings
DIALOGFLOW_LOCATION = os.getenv("DIALOGFLOW_LOCATION", "us-central1")
DIALOGFLOW_AGENT_ID = os.getenv("DIALOGFLOW_AGENT_ID", "a02eb0fe-e6a4-4815-8fa7-c832a259326f")

# Optional check: warn if file is missing
if not os.path.exists(DIALOGFLOW_KEY_PATH):
    raise FileNotFoundError(f"Dialogflow credentials file not found: {DIALOGFLOW_KEY_PATH}")
