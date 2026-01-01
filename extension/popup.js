// ===================== SPEECH SETUP =====================
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
  alert("Speech Recognition not supported in this browser");
}
const recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = false;

// ===================== SPEAK FUNCTION =====================
function speak(text) {
  if (!text || !text.trim()) {
    console.warn("Nothing to speak");
    return;
  }
  // Stop anything already speaking
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 1;
  utterance.pitch = 1;
  // Ensure voices are loaded
  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    utterance.voice = voices.find(v => v.lang === "en-US") || voices[0];
  }
  window.speechSynthesis.speak(utterance);
}

// ===================== THINKING INDICATOR =====================
function showThinking() {
  const thinkingDiv = document.getElementById("thinking");
  if (thinkingDiv) {
    thinkingDiv.style.display = "block";
  }
}

function hideThinking() {
  const thinkingDiv = document.getElementById("thinking");
  if (thinkingDiv) {
    thinkingDiv.style.display = "none";
  }
}

// ===================== SEND COMMAND WITH AI =====================
async function sendCommand(text) {
  if (!text || !text.trim()) return;

  // Show thinking indicator
  showThinking();

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        messages: [
          {
            role: "user",
            content: `You are InboxAI, a helpful voice assistant. Respond concisely and naturally to: "${text}"`
          }
        ],
      })
    });

    const data = await response.json();
    const summary = data.content
      .filter(item => item.type === "text")
      .map(item => item.text)
      .join("\n");

    // Hide thinking indicator
    hideThinking();

    // Display summary in the output area
    const outputDiv = document.getElementById("output");
    if (outputDiv) {
      outputDiv.textContent = summary;
    }

    // Speak the summary
    speak(summary);

  } catch (error) {
    hideThinking();
    console.error("Error:", error);
    const errorMsg = "Sorry, I'm having trouble processing that right now.";
    const outputDiv = document.getElementById("output");
    if (outputDiv) {
      outputDiv.textContent = errorMsg;
    }
    speak(errorMsg);
  }
}

// ===================== WINDOW ONLOAD =====================
window.onload = () => {
  // ===== GREETING =====
  speak("Hi, this is InboxAI. How can I help you?");

  // ===== SEND BUTTON =====
  const sendBtn = document.getElementById("send");
  if (sendBtn) {
    sendBtn.onclick = () => {
      const text = document.getElementById("input").value.trim();
      if (!text) return;
      sendCommand(text);
    };
  }

  // ===== MIC BUTTON =====
  const micBtn = document.getElementById("mic");
  if (micBtn && recognition) {
    micBtn.onclick = () => recognition.start();
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const inputField = document.getElementById("input");
      if (inputField) {
        inputField.value = transcript;
      }
    };
  }

  // ===== THEME TOGGLE =====
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;
  const currentTheme = localStorage.getItem("theme") || "light";
  
  if (currentTheme === "dark") {
    body.classList.add("dark");
  }
  
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      body.classList.toggle("dark");
      const theme = body.classList.contains("dark") ? "dark" : "light";
      localStorage.setItem("theme", theme);
    });
  }
};