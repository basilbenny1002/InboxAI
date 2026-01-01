import os
import base64
from typing import List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    required = [
        "GMAIL_REFRESH_TOKEN",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET"
    ]

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing OAuth env vars: {missing}")

    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    return build("gmail", "v1", credentials=creds)


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")


def extract_email_body(msg: dict) -> str:
    payload = msg.get("payload", {})

    def walk(parts):
        for part in parts:
            mime = part.get("mimeType")
            body = part.get("body", {}).get("data")

            if mime == "text/plain" and body:
                return _decode(body)

            if mime == "text/html" and body:
                soup = BeautifulSoup(_decode(body), "html.parser")
                return soup.get_text(separator=" ")

            if "parts" in part:
                found = walk(part["parts"])
                if found:
                    return found
        return ""

    if "parts" in payload:
        return walk(payload["parts"])

    if payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])

    return ""


def get_unread_emails(limit: int = 10) -> List[dict]:
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=limit
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return []

    emails = []

    for meta in messages:
        msg = service.users().messages().get(
            userId="me",
            id=meta["id"],
            format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        sender = next(
            (h["value"] for h in headers if h["name"].lower() == "from"),
            "Unknown sender"
        )

        body = extract_email_body(msg)

        if body.strip():
            emails.append({
                "sender": sender,
                "body": body
            })

    return emails
