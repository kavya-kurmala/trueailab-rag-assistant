const API_URL = "http://127.0.0.1:8000/api/chat";

let sessionId = localStorage.getItem("sessionId");

if (!sessionId) {
    sessionId = "session-" + Date.now();
    localStorage.setItem("sessionId", sessionId);
}

function addMessage(text, sender) {
    const chatBox = document.getElementById("chatBox");

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;
    messageDiv.innerText = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const loading = document.getElementById("loading");

    const message = input.value.trim();

    if (!message) {
        alert("Please enter a message");
        return;
    }

    addMessage(message, "user");
    input.value = "";
    loading.style.display = "block";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sessionId: sessionId,
                message: message
            })
        });

        const data = await response.json();

        if (data.error) {
            addMessage("Error: " + data.error, "assistant");
        } else {
            addMessage(data.reply, "assistant");
        }

    } catch (error) {
        addMessage("Backend connection failed. Please check if FastAPI is running.", "assistant");
    }

    loading.style.display = "none";
}

function newChat() {
    localStorage.removeItem("sessionId");
    location.reload();
}