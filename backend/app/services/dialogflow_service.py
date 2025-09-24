"""Dialogflow service for processing user messages and getting responses."""
import logging
import os
from pathlib import Path
from typing import Optional

from google.api_core.exceptions import InvalidArgument
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account

from app import config

logger = logging.getLogger(__name__)

# Read config values; prefer explicit configuration (app.config or env vars).
DIALOGFLOW_KEY_PATH = (getattr(config, "DIALOGFLOW_KEY_PATH", None) or
                       os.getenv("DIALOGFLOW_KEY_PATH"))
DIALOGFLOW_PROJECT_ID = (getattr(config, "DIALOGFLOW_PROJECT_ID", None) or
                         os.getenv("DIALOGFLOW_PROJECT_ID"))

# If no key path provided, fall back to a local file named "dialogflow_key.json"
# next to the package (if it exists).
if not DIALOGFLOW_KEY_PATH:
    candidate = Path(__file__).resolve().parents[1] / "dialogflow_key.json"
    if candidate.is_file():
        DIALOGFLOW_KEY_PATH = str(candidate)

if not DIALOGFLOW_KEY_PATH or not DIALOGFLOW_PROJECT_ID:
    raise RuntimeError(
        "Dialogflow configuration missing: DIALOGFLOW_KEY_PATH or "
        "DIALOGFLOW_PROJECT_ID"
    )

# Initialize Dialogflow SessionsClient using explicit service account credentials
if not os.path.isfile(DIALOGFLOW_KEY_PATH):
    error_msg = "Dialogflow credentials file not found: %s"
    logger.error(error_msg, DIALOGFLOW_KEY_PATH)
    raise FileNotFoundError(error_msg % DIALOGFLOW_KEY_PATH)

_credentials = service_account.Credentials.from_service_account_file(DIALOGFLOW_KEY_PATH)
_session_client = dialogflow.SessionsClient(credentials=_credentials)


def detect_intent_texts(text: str, session_id: Optional[str] = "demo-session",
                        language_code: str = "en") -> str:
    """Send a text query to Dialogflow and return the fulfillment text.

    Uses config values with sensible fallbacks so module import doesn't fail
    during startup.

    Args:
        text: User message text to send to Dialogflow
        session_id: Optional session identifier for conversation context
        language_code: Language code for the query (default: "en")

    Returns:
        Dialogflow response text or fallback message
    """
    try:
        # Validate input
        if not text or not text.strip():
            logger.warning("Empty text provided to detect_intent_texts")
            return "I didn't receive any message. Could you please try again?"

        # Clean and validate text length
        text = text.strip()
        if len(text) > 1000:
            logger.warning("Text too long for Dialogflow: %d characters",
                          len(text))
            return ("Your message is too long. "
                   "Please keep it under 1000 characters.")

        # Create session path
        session = _session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)

        # Create text input and query
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        logger.debug("Sending request to Dialogflow: session=%s, text='%s...'",
                    session_id, text[:50])

        # Make request to Dialogflow
        response = _session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        # Extract response
        fulfillment_text = getattr(response.query_result, "fulfillment_text", "")

        # Log intent detection results
        intent_name = getattr(response.query_result.intent, "display_name",
                             "Unknown")
        confidence = getattr(response.query_result,
                            "intent_detection_confidence", 0.0)

        logger.info("Dialogflow response - Intent: %s, Confidence: %.2f",
                   intent_name, confidence)

        # Return response or fallback
        if fulfillment_text:
            return fulfillment_text

        logger.warning("No fulfillment text from Dialogflow for input: '%s'",
                      text)
        return ("I'm sorry, I'm having trouble understanding that. "
               "Could you please rephrase your question?")

    except InvalidArgument as invalid_arg_error:
        logger.error("Dialogflow InvalidArgument error: %s", invalid_arg_error)
        return "I'm experiencing a technical issue. Please try again in a moment."
    except Exception as unexpected_error:
        logger.error("Dialogflow detect_intent failed: %s", unexpected_error,
                    exc_info=True)
        return ("I'm having trouble connecting to my knowledge base. "
               "Please try again later.")
