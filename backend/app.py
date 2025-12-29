from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_logic.email import summarize_email_logic
from services.gmail_client import get_last_email
from dotenv import load_dotenv
import os

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

# ============================ LAST GMAIL SUMMARY ============================
@app.post("/summarize/last-email")
def summarize_last_email():
    email = get_last_email()

    if not email or not email.get("body"):
        return {"summary": "No readable email found."}

    summary = summarize_email_logic(
        body=email["body"],
        sender=email.get("sender", "Unknown")
    )

    return {"summary": summary}

# ============================ COMMAND HANDLER ============================
@app.post("/command")
def handle_command(payload: CommandPayload):
    command = payload.command.lower()

    if "summarize" in command and "last email" in command:
        email = get_last_email()

        if not email or not email.get("body"):
            return {"summary": "No readable email found."}

        summary = summarize_email_logic(
            body=email["body"],
            sender=email.get("sender", "Unknown")
        )

        return {"summary": summary}

    return {"message": "Command not supported yet"}
