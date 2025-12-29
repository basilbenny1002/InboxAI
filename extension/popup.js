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
  if (!window.speechSynthesis) return;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
}

// ===================== GREETING =====================
window.onload = () => {
  speak("Hi, this is InboxAI. How can I help you?");
};

// ===================== VOICE RESULT =====================
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  document.getElementById("input").value = transcript;
  sendCommand(transcript);
};

// ===================== MIC BUTTON =====================
//document.getElementById("mic").onclick = () => {
//  recognition.start();
//};

// ===================== SEND BUTTON =====================
document.getElementById("send").onclick = () => {
  const text = document.getElementById("input").value.trim();
  if (!text) return;
  sendCommand(text);
};

// ===================== SEND COMMAND TO BACKEND =====================
async function sendCommand(commandText) {
  document.getElementById("output").innerText = "Thinking...";

  try {
    const response = await fetch(
      "https://inboxai-backend-tb5j.onrender.com/command",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          command: commandText
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    const reply = data.summary || data.message || "No response received.";

    document.getElementById("output").innerText = reply;
    speak(reply);

  } catch (err) {
    console.error(err);
    document.getElementById("output").innerText =
      "Something went wrong talking to the backend.";
    speak("Something went wrong talking to the backend.");
  }
}

// ===================== THEME TOGGLE =====================
const themeToggle = document.getElementById("themeToggle");
const body = document.body;

const currentTheme = localStorage.getItem("theme") || "light";
if (currentTheme === "dark") {
  body.classList.add("dark");
}

themeToggle.addEventListener("click", () => {
  body.classList.toggle("dark");
  const theme = body.classList.contains("dark") ? "dark" : "light";
  localStorage.setItem("theme", theme);
});
