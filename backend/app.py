from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from ai_logic.email import summarize_email_logic
from services.gmail_client import get_unread_emails   # ✅ CHANGED

load_dotenv()

app = FastAPI(title="InboxAI Backend")

# ============================ CORS ============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================ MODELS ============================
class CommandPayload(BaseModel):
    command: str

class EmailPayload(BaseModel):
    body: str
    sender: str

# ============================ HEALTH CHECK ============================
@app.get("/")
def health_check():
    return {"status": "InboxAI backend running"}

# ============================ MANUAL EMAIL SUMMARY ============================
@app.post("/summarize/email")
def summarize_email_endpoint(payload: EmailPayload):
    summary = summarize_email_logic(
        body=payload.body,
        sender=payload.sender
    )
    return {"summary": summary}

# ============================ UNREAD EMAIL SUMMARY (NEW CORE ENDPOINT) ============================
@app.post("/summarize/unread")
def summarize_unread_emails():
    emails = get_unread_emails(limit=10)

    if not emails:
        return {"summary": "You have no unread emails."}

    summaries = []

    for email in emails:
        summary = summarize_email_logic(
            body=email["body"],
            sender=email["sender"]
        )

        summaries.append({
            "sender": email["sender"],
            "summary": summary
        })

    return {
        "email_count": len(summaries),
        "summaries": summaries
    }

# ============================ COMMAND HANDLER (FIXED) ============================
@app.post("/command")
def handle_command(payload: CommandPayload):
    command = payload.command.lower()

    # ✅ Any summarize command → unread summary
    if "summarize" in command:
        return summarize_unread_emails()

    return {"message": "Command not supported yet"}
