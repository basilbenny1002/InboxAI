const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const chatContainer = document.getElementById("chatContainer");
const themeToggle = document.getElementById("themeToggle");
const body = document.body;

/* THEME */
if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark");
}

themeToggle.addEventListener("click", () => {
  body.classList.toggle("dark");
  localStorage.setItem(
    "theme",
    body.classList.contains("dark") ? "dark" : "light"
  );
});

/* SEND HANDLERS */
sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;
  chatContainer.appendChild(div);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showThinking() {
  const div = document.createElement("div");
  div.className = "thinking";
  div.id = "thinking";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatContainer.appendChild(div);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeThinking() {
  const t = document.getElementById("thinking");
  if (t) t.remove();
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  showThinking();

  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ command: text })
    });

    const data = await res.json();
    removeThinking();

    let reply = "";

    if (data.summaries && Array.isArray(data.summaries)) {
      reply = data.summaries
        .map(s => `📧 ${s.sender}: ${s.summary}`)
        .join("\n\n");
    } 
    else if (data.summary) {
      reply = `📧 ${data.sender}: ${data.summary}`;
    } 
    else if (data.error) {
      reply = data.error;
    } 
    else {
      reply = "No readable response received.";
    }

    addMessage(reply, "bot");

  } catch (err) {
    removeThinking();
    console.error(err);
    addMessage("⚠️ Backend not responding.", "bot");
  }
}
