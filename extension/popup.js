// ===================== SPEECH SETUP =====================
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  alert("Speech Recognition not supported in this browser");
}

const recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = false;

// ===================== SPEAK FUNCTION =====================
function speak(text) {
  if (!text || !text.trim()) return;

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1;
  utterance.pitch = 1;

  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    utterance.voice = voices.find(v => v.lang === "en-US") || voices[0];
  }

  window.speechSynthesis.speak(utterance);
}

// ===================== THINKING INDICATOR =====================
function showThinking() {
  const el = document.getElementById("thinking");
  if (el) el.style.display = "block";
}

function hideThinking() {
  const el = document.getElementById("thinking");
  if (el) el.style.display = "none";
}

// ===================== SEND COMMAND =====================
async function sendCommand(command) {
  if (!command || !command.trim()) return;

  const responseBox = document.getElementById("response");

  // 1️⃣ PRINT + SPEAK ACKNOWLEDGEMENT
  const ack = `Alright, I’ll ${command}.`;
  responseBox.textContent = ack;
  speak(ack);

  // 2️⃣ SHOW THINKING
  showThinking();

  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command })
    });

    const data = await res.json();
    hideThinking();

    let finalText = "";

    // 3️⃣ FORMAT BACKEND RESPONSE
    if (data.summaries && Array.isArray(data.summaries)) {
      finalText = data.summaries
        .map(
          s => `Summary of email from ${s.sender}: ${s.summary}`
        )
        .join("\n\n");
    } 
    else if (data.summary) {
      finalText = `Summary of email from ${data.sender}: ${data.summary}`;
    } 
    else if (data.error) {
      finalText = data.error;
    } 
    else {
      finalText = "No readable response received.";
    }

    // 4️⃣ PRINT + SPEAK FINAL RESPONSE
    responseBox.textContent = finalText;
    speak(finalText);

  } catch (err) {
    hideThinking();
    console.error(err);

    const msg = "Something went wrong while talking to the backend.";
    responseBox.textContent = msg;
    speak(msg);
  }
}

// ===================== VOICE INPUT =====================
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const input = document.getElementById("input");
  if (input) input.value = transcript;
  sendCommand(transcript);
};

// ===================== WINDOW ONLOAD =====================
window.onload = () => {
  // Greeting
  speak("Hi, this is InboxAI. How can I help you?");

  // Send button
  const sendBtn = document.getElementById("send");
  if (sendBtn) {
    sendBtn.onclick = () => {
      const text = document.getElementById("input").value.trim();
      sendCommand(text);
    };
  }

  // Mic button
  const micBtn = document.getElementById("mic");
  if (micBtn) {
    micBtn.onclick = () => recognition.start();
  }

  // Theme toggle
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;
  const currentTheme = localStorage.getItem("theme") || "light";

  if (currentTheme === "dark") body.classList.add("dark");

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      body.classList.toggle("dark");
      localStorage.setItem(
        "theme",
        body.classList.contains("dark") ? "dark" : "light"
      );
    });
  }
};
