document.getElementById("send").onclick = async () => {
  const text = document.getElementById("input").value;
  document.getElementById("output").innerText = "Sending...";

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/summarize/email",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          body: text,
          sender: "Gmail"
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    document.getElementById("output").innerText = data.summary;

  } catch (err) {
    console.error("FULL ERROR:", err);
    document.getElementById("output").innerText =
      err.message || "Backend error";
  }
};


// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
if (currentTheme === 'dark') {
  body.classList.add('dark');
}

themeToggle.addEventListener('click', () => {
  body.classList.toggle('dark');
  const theme = body.classList.contains('dark') ? 'dark' : 'light';
  localStorage.setItem('theme', theme);
});

// Your existing code below
document.getElementById("send").onclick = async () => {
  const text = document.getElementById("input").value;
  document.getElementById("output").innerText = "Sending...";
  // ... rest of your code
};