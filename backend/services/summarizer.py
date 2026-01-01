import re
from services.llm_client import call_llm

def clean_email(text: str) -> str:
    text = re.sub(r"\ufeff|\u2007", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(unsubscribe|click here|tap to apply)", "", text, flags=re.I)
    return text.strip()


def summarize_email(body: str, sender: str) -> str:
    body = clean_email(body)

    prompt = f"""
Summarize the following email.

Rules:
- Do NOT say phrases like "Here is the summary", "This email is about", or "In 2-3 sentences"
- Write only the summary content directly
- Be concise and factual
- No introductions, no meta commentary

Email sender: {sender}

Email body:
{body}
"""


    return call_llm(prompt)
