"""Dialogflow CX service for processing user messages and getting responses."""
import logging
import os
from pathlib import Path
from typing import Optional

from google.api_core.exceptions import InvalidArgument
from google.cloud.dialogflowcx_v3 import SessionsClient
from google.cloud.dialogflowcx_v3.types import DetectIntentRequest, QueryInput, TextInput
from google.oauth2 import service_account

from app import config

logger = logging.getLogger(__name__)

# Read config values; prefer explicit configuration (app.config or env vars).
DIALOGFLOW_KEY_PATH = (getattr(config, "DIALOGFLOW_KEY_PATH", None) or
                       os.getenv("DIALOGFLOW_KEY_PATH"))
DIALOGFLOW_PROJECT_ID = (getattr(config, "DIALOGFLOW_PROJECT_ID", None) or
                         os.getenv("DIALOGFLOW_PROJECT_ID"))
DIALOGFLOW_LOCATION = (getattr(config, "DIALOGFLOW_LOCATION", None) or
                       os.getenv("DIALOGFLOW_LOCATION", "global"))
DIALOGFLOW_AGENT_ID = (getattr(config, "DIALOGFLOW_AGENT_ID", None) or
                       os.getenv("DIALOGFLOW_AGENT_ID"))

# If no key path provided, fall back to a local file named "dialogflow_key.json"
# next to the package (if it exists).
if not DIALOGFLOW_KEY_PATH:
    candidate = Path(__file__).resolve().parents[2] / "dialogflow_key.json"
    if candidate.is_file():
        DIALOGFLOW_KEY_PATH = str(candidate)

if not DIALOGFLOW_KEY_PATH or not DIALOGFLOW_PROJECT_ID:
    raise RuntimeError(
        "Dialogflow configuration missing: DIALOGFLOW_KEY_PATH or "
        "DIALOGFLOW_PROJECT_ID"
    )

# Initialize Dialogflow CX SessionsClient using explicit service account credentials
if not os.path.isfile(DIALOGFLOW_KEY_PATH):
    error_msg = "Dialogflow credentials file not found: %s"
    logger.error(error_msg, DIALOGFLOW_KEY_PATH)
    raise FileNotFoundError(error_msg % DIALOGFLOW_KEY_PATH)

_credentials = service_account.Credentials.from_service_account_file(DIALOGFLOW_KEY_PATH)

# Configure client with regional endpoint
client_options = None
if DIALOGFLOW_LOCATION and DIALOGFLOW_LOCATION != "global":
    from google.api_core.client_options import ClientOptions
    api_endpoint = f"{DIALOGFLOW_LOCATION}-dialogflow.googleapis.com"
    client_options = ClientOptions(api_endpoint=api_endpoint)
    logger.info("Using regional endpoint: %s", api_endpoint)

_session_client = SessionsClient(
    credentials=_credentials,
    client_options=client_options
)


def detect_intent_texts(text: str, session_id: Optional[str] = "demo-session",
                        language_code: str = "en") -> str:
    """Send a text query to Dialogflow CX and return the response text.

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

        # Check if agent ID is configured
        if not DIALOGFLOW_AGENT_ID:
            logger.error("DIALOGFLOW_AGENT_ID not configured")
            return ("The chatbot is not fully configured. "
                   "Please set DIALOGFLOW_AGENT_ID environment variable.")

        # Create session path for Dialogflow CX
        session_path = (
            f"projects/{DIALOGFLOW_PROJECT_ID}/"
            f"locations/{DIALOGFLOW_LOCATION}/"
            f"agents/{DIALOGFLOW_AGENT_ID}/"
            f"sessions/{session_id}"
        )

        logger.info("DEBUG - Project: %s, Location: %s, Agent: %s",
                   DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LOCATION, DIALOGFLOW_AGENT_ID)
        logger.info("DEBUG - Full session path: %s", session_path)

        # Create text input and query
        text_input = TextInput(text=text)
        query_input = QueryInput(text=text_input, language_code=language_code)

        # Create request
        request = DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )

        logger.debug("Sending request to Dialogflow CX: session=%s, text='%s...'",
                    session_id, text[:50])

        # Make request to Dialogflow CX
        response = _session_client.detect_intent(request=request)

        # Extract response messages
        response_messages = response.query_result.response_messages
        fulfillment_text = ""

        # Combine all text responses
        for message in response_messages:
            if message.text and message.text.text:
                fulfillment_text += " ".join(message.text.text) + " "

        fulfillment_text = fulfillment_text.strip()

        # Log intent detection results
        logger.info("Dialogflow CX response received: %s...",
                   fulfillment_text[:100] if fulfillment_text else "empty")

        # Return response or fallback
        if fulfillment_text:
            return fulfillment_text

        logger.warning("No fulfillment text from Dialogflow CX for input: '%s'",
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
