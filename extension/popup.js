// ===================== ELEMENTS =====================
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const chatMessages = document.getElementById("chatMessages");
const themeToggle = document.getElementById("themeToggle");
const body = document.body;

// ===================== THEME =====================
const savedTheme = localStorage.getItem("theme") || "light";
if (savedTheme === "dark") body.classList.add("dark");

themeToggle.addEventListener("click", () => {
  body.classList.toggle("dark");
  localStorage.setItem(
    "theme",
    body.classList.contains("dark") ? "dark" : "light"
  );
});

// ===================== SPEECH (FIXED) =====================
let voices = [];
let speechUnlocked = false;

// Load voices properly
function loadVoices() {
  voices = window.speechSynthesis.getVoices();
}

window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

// 🔓 Unlock speech on first user interaction
document.addEventListener("click", () => {
  if (!speechUnlocked) {
    const unlock = new SpeechSynthesisUtterance(" ");
    unlock.volume = 0;
    window.speechSynthesis.speak(unlock);
    speechUnlocked = true;
  }
}, { once: true });

function speak(text) {
  if (!speechUnlocked || !text.trim()) return;

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1;
  utterance.pitch = 1;

  const voice =
    voices.find(v => v.lang === "en-US") ||
    voices.find(v => v.lang.startsWith("en")) ||
    voices[0];

  if (voice) utterance.voice = voice;

  window.speechSynthesis.speak(utterance);
}

// ===================== CHAT =====================
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  scrollToBottom();

  if (type === "bot") {
    speak(text);
  }
}

function showThinking() {
  const div = document.createElement("div");
  div.className = "thinking";
  div.id = "thinking";
  div.innerHTML = `
    <div class="thinking-dots">
      <span></span><span></span><span></span>
    </div>
    <p>Thinking...</p>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function removeThinking() {
  const t = document.getElementById("thinking");
  if (t) t.remove();
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===================== SEND COMMAND =====================
async function sendCommand() {
  const command = input.value.trim();
  if (!command) return;

  addMessage(command, "user");
  input.value = "";

  showThinking();

  try {
    const res = await fetch("https://inboxai-backend-tb5j.onrender.com/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command })
    });

    const data = await res.json();
    removeThinking();

    let reply = "";

    if (data.summaries && Array.isArray(data.summaries)) {
      reply = data.summaries
        .map(s => `📧 ${s.sender}: ${s.summary}`)
        .join("\n\n");
    } else if (data.summary) {
      reply = `📧 ${data.sender}: ${data.summary}`;
    } else if (data.error) {
      reply = data.error;
    } else {
      reply = "No readable response received.";
    }

    addMessage(reply, "bot");

  } catch (err) {
    removeThinking();
    console.error(err);
    addMessage("Backend not responding.", "bot");
  }
}

// ===================== EVENTS =====================
sendBtn.addEventListener("click", sendCommand);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendCommand();
  }
});

// ===================== GREETING =====================
const greetingText = "Hi, this is InboxAI. How can I help you?";

window.onload = () => {
  // show greeting text immediately
  const div = document.createElement("div");
  div.className = "message bot";
  div.textContent = greetingText;
  chatMessages.appendChild(div);
  scrollToBottom();
};

// 🔓 After first user interaction → speak greeting
document.addEventListener("click", () => {
  if (!speechUnlocked) {
    const unlock = new SpeechSynthesisUtterance(" ");
    unlock.volume = 0;
    window.speechSynthesis.speak(unlock);
    speechUnlocked = true;
  }

  speak(greetingText);
}, { once: true });
