from flask import Blueprint, request, jsonify
from app.services.dialogflow_service import detect_intent_texts

# Create the blueprint object
bp = Blueprint("routes", __name__)

@bp.route("/chat", methods=["POST"])
def chat():
    """
    POST /chat
    Body: { "message": "Hello" }
    Response: { "response": "Hi there!" }
    """
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response_text = detect_intent_texts(user_input)
    return jsonify({"response": response_text})
