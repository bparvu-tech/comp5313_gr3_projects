function generateSessionId() {
  return (
    "session_" +
    Date.now() +
    "_" +
    Math.random().toString(36).substr(2, 9)
  );
}

const SESSION_ROTATION_LIMIT = 4;
let messagesSinceLastSession = 0;

const CONFIG = {
  apiEndpoint: "/api/v1/chat/",
  sessionId: generateSessionId(),
};

function createNewSessionId() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : generateSessionId();
}

function rotateSessionIfNeeded() {
  messagesSinceLastSession += 1;
  if (messagesSinceLastSession >= SESSION_ROTATION_LIMIT) {
    CONFIG.sessionId = createNewSessionId();
    messagesSinceLastSession = 0;
    console.log("Rotated session ID:", CONFIG.sessionId);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const chatPopup = document.getElementById("chat-popup");
  const chatToggle = document.getElementById("chat-toggle");
  const chatClose = document.getElementById("chat-close");
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const chatReset = document.getElementById("chat-reset");

  if (!chatBox || !userInput || !sendBtn) {
    console.error("Chat DOM elements not found");
    return;
  }

  function appendMessage(sender, text) {
    const msg = document.createElement("div");
    msg.innerHTML = `<b>${sender}:</b> ${text}`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function resetChat() {
    chatBox.innerHTML = "";

    const welcome = document.querySelector(".chat-welcome");
    if (welcome) {
      welcome.style.display = "block";
    }

    chatBox.scrollTop = 0;

    CONFIG.sessionId = createNewSessionId();
    messagesSinceLastSession = 0;
    console.log("Chat reset, new session ID:", CONFIG.sessionId);
  }

// --- Main send function ---
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  userInput.disabled = true;
  sendBtn.disabled = true;

  // Show user message
  appendMessage("You", message);
  userInput.value = "";

  // Hide welcome after first real message
  const welcome = document.querySelector(".chat-welcome");
  if (welcome) welcome.style.display = "none";

  // Add "Thinking..." placeholder
  const thinkingDiv = document.createElement("div");
  thinkingDiv.id = "assistant-thinking";
  thinkingDiv.innerHTML =
    `<b>ThunderwolfBot:</b> <span class="thinking-text">Thinking<span class="thinking-dots"></span></span>`;
  chatBox.appendChild(thinkingDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  const MIN_THINKING_MS = 1800;
  const startTime = Date.now();

  try {
    const response = await fetch(CONFIG.apiEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        session_id: CONFIG.sessionId,
      }),
    });

    if (!response.ok) {
      let errorMsg = `Server error: ${response.status}`;
      try {
        const errData = await response.json();
        if (errData && errData.message) {
          errorMsg = errData.message;
        }
      } catch {
        /* ignore JSON errors */
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    let reply = (data.response || data.reply || "").trim();

    if (!reply) {
      reply =
        "I didn't catch this information, try asking in a different way.";
    }

    // Markdown → HTML
    let replyHtml;
    try {
      replyHtml = marked.parse(reply);
    } catch (e) {
      console.error("Markdown parse error:", e);
      replyHtml = reply;
    }

    const elapsed = Date.now() - startTime;
    if (elapsed < MIN_THINKING_MS) {
      await new Promise((res) => setTimeout(res, MIN_THINKING_MS - elapsed));
    }

    // Use ThunderwolfBot + formatted HTML
    thinkingDiv.innerHTML = `<b>ThunderwolfBot:</b> ${replyHtml}`;
    chatBox.scrollTop = chatBox.scrollHeight;

    rotateSessionIfNeeded();
  } catch (error) {
    console.error("Chat error:", error);

    const elapsed = Date.now() - startTime;
    if (elapsed < MIN_THINKING_MS) {
      await new Promise((res) => setTimeout(res, MIN_THINKING_MS - elapsed));
    }

    thinkingDiv.innerHTML =
      `<b>ThunderwolfBot:</b> I'm having trouble connecting right now. ` +
      `Please make sure the backend server is running and try again.`;
    chatBox.scrollTop = chatBox.scrollHeight;
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}


  // --- Wire events ---
  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

  document.querySelectorAll(".chat-quick-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const question = btn.dataset.question;
      userInput.value = question;
      sendMessage();

      const welcome = document.querySelector(".chat-welcome");
      if (welcome) welcome.style.display = "none";
    });
  });

  if (chatReset) {
    chatReset.addEventListener("click", resetChat);
  }

  if (chatClose && chatToggle && chatPopup) {
    chatClose.addEventListener("click", () => {
      chatPopup.style.display = "none";
      chatToggle.style.display = "block";
    });

    chatToggle.addEventListener("click", () => {
      chatPopup.style.display = "flex";
      chatToggle.style.display = "none";
    });
  }

  // Show popup on first load
  if (chatPopup) {
    chatPopup.style.display = "flex";
  }
  if (chatToggle) {
    chatToggle.style.display = "none";
  }

  console.log("Chatbot initialized");
  console.log("Session ID:", CONFIG.sessionId);
  console.log("API Endpoint:", CONFIG.apiEndpoint);
});