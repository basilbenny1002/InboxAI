from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback

from services.gmail_client import get_unread_emails
from ai_logic.email import summarize_email_logic
from services.llm_client import intelligent_command_handler

load_dotenv()

app = FastAPI(title="InboxAI Backend")

# ============================ CORS ============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================ MODELS ============================
class CommandPayload(BaseModel):
    command: str


# ============================ ROOT ============================
@app.get("/")
def root():
    return {"status": "InboxAI backend running", "docs": "/docs"}


# ============================ HELPER FUNCTIONS ============================
def get_unread_emails_summary():
    """Get all unread emails with summaries"""
    try:
        print("\n=== Starting get_unread_emails_summary ===")
        emails = get_unread_emails()
        print(f"Retrieved {len(emails)} emails from Gmail")

        if not emails:
            return {"email_count": 0, "summaries": []}

        summaries = []
        for idx, email in enumerate(emails, start=1):
            print(f"\nProcessing email {idx}/{len(emails)}")
            print(f"  Sender: {email['sender']}")
            print(f"  Attachments: {len(email.get('attachments', []))}")
            
            try:
                summary = summarize_email_logic(
                    body=email["body"],
                    sender=email["sender"],
                    attachments=email.get("attachments", [])
                )
                
                # Include attachment info in response
                attachment_info = ""
                if email.get("attachments"):
                    att_count = len(email["attachments"])
                    att_names = [a['filename'] for a in email["attachments"]]
                    attachment_info = f" (with {att_count} attachment{'s' if att_count > 1 else ''}: {', '.join(att_names)})"
                
                summaries.append({
                    "summary_number": idx,
                    "sender": email["sender"],
                    "summary": summary,
                    "has_attachments": len(email.get("attachments", [])) > 0,
                    "attachment_count": len(email.get("attachments", [])),
                    "attachment_info": attachment_info
                })
                
                print(f"  ✓ Summary generated successfully")
                
            except Exception as e:
                print(f"  ✗ Error summarizing email: {str(e)}")
                traceback.print_exc()
                
                # Add a fallback summary instead of failing completely
                summaries.append({
                    "summary_number": idx,
                    "sender": email["sender"],
                    "summary": f"[Error generating summary: {str(e)}]",
                    "has_attachments": len(email.get("attachments", [])) > 0,
                    "attachment_count": len(email.get("attachments", [])),
                    "attachment_info": ""
                })

        print(f"\n=== Completed: {len(summaries)} summaries generated ===")
        
        return {
            "email_count": len(summaries),
            "summaries": summaries
        }
    
    except Exception as e:
        print(f"\n!!! ERROR in get_unread_emails_summary !!!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def get_last_email_summary():
    """Get the last unread email with summary"""
    try:
        print("\n=== Starting get_last_email_summary ===")
        emails = get_unread_emails(max_results=1)

        if not emails:
            return {"error": "No unread emails found"}

        email = emails[0]
        print(f"Processing email from: {email['sender']}")
        
        summary = summarize_email_logic(
            body=email["body"],
            sender=email["sender"],
            attachments=email.get("attachments", [])
        )

        return {
            "sender": email["sender"],
            "summary": summary,
            "has_attachments": len(email.get("attachments", [])) > 0,
            "attachment_count": len(email.get("attachments", []))
        }
    
    except Exception as e:
        print(f"\n!!! ERROR in get_last_email_summary !!!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================ COMMAND HANDLER ============================
@app.post("/command")
def handle_command(payload: CommandPayload):
    """
    Intelligent command handler using LLM function calling
    """
    try:
        # Map function names to actual Python functions
        function_map = {
            "get_unread_emails_summary": get_unread_emails_summary,
            "get_last_email_summary": get_last_email_summary
        }
        
        # Use intelligent handler
        result = intelligent_command_handler(payload.command, function_map)
        
        return result
    
    except Exception as e:
        print(f"\n!!! ERROR in handle_command !!!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================ OLD ENDPOINTS ============================
@app.post("/summarize/unread")
def summarize_unread_emails():
    """Legacy endpoint for summarizing unread emails"""
    try:
        return get_unread_emails_summary()
    except Exception as e:
        print(f"\n!!! ERROR in /summarize/unread endpoint !!!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))