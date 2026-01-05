from services.llm_client import call_llm

MAX_BODY_CHARS = 2000
MAX_ATTACHMENT_CHARS = 1000


def summarize_email_logic(body: str, sender: str, subject: str = "", attachments: str = ""):
    """
    Summarize email body and attachments in a natural, conversational way
    """

    # ---- TRUNCATION (THIS WAS THE ISSUE) ----
    if body and len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS] + "\n...(truncated)"

    if attachments and len(attachments) > MAX_ATTACHMENT_CHARS:
        attachments = attachments[:MAX_ATTACHMENT_CHARS] + "\n...(truncated)"

    print(f"\n=== Summarizing email from {sender} ===")
    print(f"Subject: {subject}")
    print(f"Body length: {len(body)} chars")
    print(f"Attachment text length: {len(attachments)} chars")

    context_parts = []

    if subject and subject.strip():
        context_parts.append(f"Subject: {subject}")

    if body and body.strip():
        context_parts.append(f"\nEmail Body:\n{body}")
    else:
        context_parts.append("\nEmail Body:\n[No body text]")

    if attachments and attachments.strip():
        context_parts.append(f"\nAttachments:\n{attachments}")

    full_prompt = f"""
You're a friendly email assistant. Summarize this email naturally and conversationally.

Keep it brief (1–2 sentences). No links, no tech talk.

Email from: {sender}

{chr(10).join(context_parts)}

Quick summary:
"""

    try:
        summary = call_llm(full_prompt)
        return summary.strip()
    except Exception as e:
        print(f"LLM error: {e}")
        if body:
            return f"It's about {body[:80]}..."
        elif subject:
            return f"Email about: {subject}"
        else:
            return "Email received."
