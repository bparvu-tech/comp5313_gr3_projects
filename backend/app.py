from flask import Flask, request, jsonify
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account

app = Flask(__name__)

CREDENTIALS_PATH = "dialogflow_key.json"
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

DIALOGFLOW_PROJECT_ID = "lu-assistant-bot"
SESSION_ID = "chat-bot-session"

session_client = dialogflow.SessionsClient(credentials=credentials)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

    text_input = dialogflow.TextInput(text=user_message, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    bot_reply = response.query_result.fulfillment_text
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
