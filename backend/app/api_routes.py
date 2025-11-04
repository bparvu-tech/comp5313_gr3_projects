"""API routes with automatic documentation for the Lakehead University Chatbot backend."""
import logging
from datetime import datetime

from flask import request
from flask_restx import Api, Resource, fields, Namespace

from app.services.dialogflow_service import detect_intent_texts

# Configure logging
logger = logging.getLogger(__name__)

# Create API and namespaces
api = Api(
    title='Lakehead University Chatbot API',
    version='1.0',
    description='REST API for the Lakehead University Chatbot backend',
    doc='/docs/',  # Swagger UI will be available at /docs/
    prefix='/api/v1'
)

# Create namespaces for organizing endpoints
health_ns = Namespace('health', description='Health check operations')
chat_ns = Namespace('chat', description='Chat operations')

# Add namespaces to API
api.add_namespace(health_ns)
api.add_namespace(chat_ns)

# Define data models for request/response validation and documentation
health_response_model = api.model('HealthResponse', {
    'status': fields.String(required=True, description='Service status', example='healthy'),
    'service': fields.String(required=True, description='Service name', example='lakehead-chatbot-backend'),
    'version': fields.String(required=True, description='API version', example='prototype-1')
})

chat_request_model = api.model('ChatRequest', {
    'message': fields.String(
        required=True,
        description='User message to send to the chatbot',
        example='Hello, what programs does Lakehead University offer?',
        min_length=1,
        max_length=1000
    ),
    'session_id': fields.String(
        required=False,
        description='Optional session identifier for conversation context',
        example='user-session-123',
        default='default-session'
    )
})

chat_response_model = api.model('ChatResponse', {
    'response': fields.String(
        required=True,
        description='Chatbot response message',
        example='Lakehead University offers various programs including Computer Science, Engineering, Business, and more.'
    ),
    'session_id': fields.String(
        required=True,
        description='Session identifier used for this conversation',
        example='user-session-123'
    ),
    'timestamp': fields.String(
        required=True,
        description='ISO timestamp of the response',
        example='2025-01-27T20:40:47.080034Z'
    )
})

error_model = api.model('ErrorResponse', {
    'error': fields.String(
        required=True,
        description='Error type or message',
        example='Bad Request'
    ),
    'message': fields.String(
        required=True,
        description='Detailed error message',
        example='Message cannot be empty'
    )
})


@health_ns.route('/')
class HealthCheck(Resource):
    """Health check endpoint for monitoring service status."""

    @health_ns.doc('get_health')
    @health_ns.marshal_with(health_response_model, code=200)
    def get(self):
        """Get service health status.

        Returns the current status of the Lakehead University Chatbot service,
        including service name and version information.

        This endpoint can be used for:
        - Health monitoring
        - Load balancer health checks
        - Service discovery
        """
        return {
            'status': 'healthy',
            'service': 'lakehead-chatbot-backend',
            'version': 'prototype-1'
        }, 200


@chat_ns.route('/')
class Chat(Resource):
    """Chat endpoint for processing user messages through Dialogflow."""

    @chat_ns.doc('post_chat')
    @chat_ns.expect(chat_request_model, validate=False)
    def post(self):  # pylint: disable=too-many-return-statements
        """Process a chat message through Dialogflow.

        Send a user message to the Lakehead University Chatbot and receive
        a response processed through Google Dialogflow.

        **Request Body:**
        - `message` (required): The user's message (1-1000 characters)
        - `session_id` (optional): Session identifier for conversation context

        **Response:**
        - `response`: The chatbot's reply
        - `session_id`: Session identifier used
        - `timestamp`: When the response was generated

        **Error Codes:**
        - 400: Invalid request (empty message, message too long, invalid JSON)
        - 500: Internal server error (Dialogflow connection issues)
        """
        try:
            # Get request data
            data = request.get_json() or {}
            user_input = data.get("message", "").strip()
            session_id = data.get("session_id", "default-session")

            # Validate input
            if not user_input:
                return {
                    "error": "Bad Request",
                    "message": "Message cannot be empty"
                }, 400

            if len(user_input) > 1000:
                return {
                    "error": "Bad Request",
                    "message": "Message is too long (max 1000 characters)"
                }, 400

            logger.info("Processing message from session %s: %s...",
                       session_id, user_input[:50])

            # Get response from Dialogflow
            response_text = detect_intent_texts(user_input, session_id)

            if not response_text:
                logger.warning("Empty response from Dialogflow for message: %s",
                              user_input)
                response_text = ("I'm sorry, I didn't understand that. "
                               "Could you please rephrase your question?")

            logger.info("Response sent to session %s: %s...",
                       session_id, response_text[:50])

            return {
                "response": response_text,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }, 200

        except (ValueError, TypeError) as validation_error:
            logger.error("Validation error in chat request: %s", validation_error)
            return {
                "error": "Invalid request data",
                "message": "Please check your request format."
            }, 400
        except (ConnectionError, TimeoutError) as connection_error:
            logger.error("Connection error processing chat request: %s",
                        connection_error, exc_info=True)
            return {
                "error": "Service temporarily unavailable",
                "message": "Please try again in a moment."
            }, 503
        except Exception as unexpected_error:  # pylint: disable=broad-exception-caught
            logger.error("Unexpected error processing chat request: %s",
                        unexpected_error, exc_info=True)
            return {
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again."
            }, 500


# Legacy routes for backward compatibility
@api.route('/health')
class LegacyHealthCheck(Resource):
    """Legacy health check endpoint (without /api/v1 prefix)."""

    @api.doc('legacy_get_health')
    @api.marshal_with(health_response_model, code=200)
    def get(self):
        """Legacy health check endpoint.

        This endpoint is maintained for backward compatibility.
        Use /api/v1/health/ for new integrations.
        """
        return {
            'status': 'healthy',
            'service': 'lakehead-chatbot-backend',
            'version': 'prototype-1'
        }, 200


@api.route('/chat')
class LegacyChat(Resource):
    """Legacy chat endpoint (without /api/v1 prefix)."""

    @api.doc('legacy_post_chat')
    @api.expect(chat_request_model, validate=True)
    @api.marshal_with(chat_response_model, code=200)
    @api.marshal_with(error_model, code=400)
    @api.marshal_with(error_model, code=500)
    def post(self):  # pylint: disable=too-many-return-statements
        """Legacy chat endpoint.

        This endpoint is maintained for backward compatibility.
        Use /api/v1/chat/ for new integrations.
        """
        # Delegate to the main chat implementation
        chat_resource = Chat()
        return chat_resource.post()
