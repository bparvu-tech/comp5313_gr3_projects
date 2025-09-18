import logging
import os
from typing import Optional
from pathlib import Path

from google.cloud import dialogflow_v2 as dialogflow
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account

from app import config

logger = logging.getLogger(__name__)

# Read config values; prefer explicit configuration (app.config or env vars).
DIALOGFLOW_KEY_PATH = getattr(config, "DIALOGFLOW_KEY_PATH", None) or os.getenv("DIALOGFLOW_KEY_PATH")
DIALOGFLOW_PROJECT_ID = getattr(config, "DIALOGFLOW_PROJECT_ID", None) or os.getenv("DIALOGFLOW_PROJECT_ID")

# If no key path provided, fall back to a local file named "dialogflow_key.json" next to the package (if it exists).
if not DIALOGFLOW_KEY_PATH:
    candidate = Path(__file__).resolve().parents[1] / "dialogflow_key.json"
    if candidate.is_file():
        DIALOGFLOW_KEY_PATH = str(candidate)

if not DIALOGFLOW_KEY_PATH or not DIALOGFLOW_PROJECT_ID:
    raise RuntimeError("Dialogflow configuration missing: DIALOGFLOW_KEY_PATH or DIALOGFLOW_PROJECT_ID")

# Initialize Dialogflow SessionsClient using explicit service account credentials
if not os.path.isfile(DIALOGFLOW_KEY_PATH):
    msg = f"Dialogflow credentials file not found: {DIALOGFLOW_KEY_PATH}"
    logger.error(msg)
    raise FileNotFoundError(msg)

_credentials = service_account.Credentials.from_service_account_file(DIALOGFLOW_KEY_PATH)
_session_client = dialogflow.SessionsClient(credentials=_credentials)


def detect_intent_texts(text: str, session_id: Optional[str] = "demo-session", language_code: str = "en") -> str:
    """Send a text query to Dialogflow and return the fulfillment text.

    Uses config values with sensible fallbacks so module import doesn't fail during startup.
    """
    session = _session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = _session_client.detect_intent(request={"session": session, "query_input": query_input})
        return getattr(response.query_result, "fulfillment_text", "")
    except InvalidArgument:
        logger.exception("Dialogflow InvalidArgument")
        return "Dialogflow request failed."
    except Exception:
        logger.exception("Dialogflow detect_intent failed")
        raise
