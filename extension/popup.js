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
    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = '<div class="thinking"><div class="thinking-dots"><span></span><span></span><span></span></div><p>Thinking...</p></div>';
    responseDiv.style.display = "block";
}

function hideThinking() {
    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = '';
}

function showSummary(summary) {
    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = `<div class="summary"><p>${summary}</p></div>`;
    responseDiv.style.display = "block";
    speak(summary);
}

// ===================== SIMULATED AI PROCESSING =====================
async function processCommand(text) {
    // Simulate API call/processing time
    return new Promise(resolve => {
        setTimeout(() => {
            // This is a mock response - replace with actual AI API call
            const mockResponses = [
                "I've analyzed your request and here's what I found...",
                "Based on my analysis, I recommend the following...",
                "I've processed your query and the summary is...",
                "After careful consideration, here are my thoughts..."
            ];
            const randomResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
            resolve(`${randomResponse} For "${text}", I would suggest checking your email priorities first.`);
        }, 2000); // 2 second delay to simulate thinking
    });
}

// ===================== SEND COMMAND =====================
async function sendCommand(text) {
    if (!text) return;
    
    // Clear input
    document.getElementById("input").value = '';
    
    // Show thinking indicator
    showThinking();
    
    // Process the command
    const summary = await processCommand(text);
    
    // Hide thinking and show summary
    hideThinking();
    showSummary(summary);
}

// ===================== INITIALIZATION =====================
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
        
        // Also allow Enter key in input field
        document.getElementById("input").addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                const text = document.getElementById("input").value.trim();
                if (!text) return;
                sendCommand(text);
            }
        });
    }
    
    // ===== MIC BUTTON =====
    const micBtn = document.getElementById("mic");
    if (micBtn && recognition) {
        micBtn.onclick = () => recognition.start();
        
        // Handle speech recognition result
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById("input").value = transcript;
            sendCommand(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
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