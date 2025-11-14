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
DIALOGFLOW_PROJECT_ID = os.getenv(
    "DIALOGFLOW_PROJECT_ID",
    "comp5313-chatbot-473118")

# Dialogflow CX Agent settings
DIALOGFLOW_LOCATION = os.getenv("DIALOGFLOW_LOCATION", "us-central1")
DIALOGFLOW_AGENT_ID = os.getenv(
    "DIALOGFLOW_AGENT_ID",
    "a02eb0fe-e6a4-4815-8fa7-c832a259326f")

# Optional check: warn if file is missing
if not os.path.exists(DIALOGFLOW_KEY_PATH):
    raise FileNotFoundError(
        f"Dialogflow credentials file not found: {DIALOGFLOW_KEY_PATH}")

# Retrieval-Augmented Generation (RAG) configuration
_default_data_dir = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "data",
        "lakehead_scraped"))
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
RAG_DATA_DIR = os.getenv("RAG_DATA_DIR", _default_data_dir)
RAG_MAX_DOCS = int(os.getenv("RAG_MAX_DOCS", "500"))
RAG_MIN_SIMILARITY = float(os.getenv("RAG_MIN_SIMILARITY", "0.22"))
RAG_MIN_CONFIDENCE = float(os.getenv("RAG_MIN_CONFIDENCE", "0.55"))
