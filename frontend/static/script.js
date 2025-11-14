// Get references to HTML elements
const chatBox = document.getElementById('chat-box');   // div where messages appear
const userInput = document.getElementById('user-input'); // input field
const sendBtn = document.getElementById('send-btn');     // send button

// Function to append messages to chat box
function appendMessage(sender, text) {
  const msg = document.createElement('div');
  msg.innerHTML = `<b>${sender}:</b> ${text}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight; // scroll to bottom
}

// Function to send user message to Flask backend
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage('You', message);   // show user message
  userInput.value = '';            // clear input field

  try {
    // Send POST request to Flask /chat endpoint
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })  // must match app.py expectation
    });

    const data = await response.json();
    appendMessage('Bot', data.reply);  // display Flask/Dialogflow reply

  } catch (err) {
    console.error('Error:', err);
    appendMessage('Bot', 'Sorry, something went wrong.');
  }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});
