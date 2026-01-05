from services.llm_client import call_llm

MAX_CATEGORY_BODY_CHARS = 500

def get_email_category(body: str, sender: str, subject: str = "") -> str:
    # Trim body aggressively (categorization does NOT need more)
    if body and len(body) > MAX_CATEGORY_BODY_CHARS:
        body = body[:MAX_CATEGORY_BODY_CHARS] + "..."

    prompt = (
        "Categorize the email into ONE category:\n"
        "Primary, Promotions, Social, Spam, Updates\n\n"
        f"Sender: {sender}\n"
        f"Subject: {subject}\n"
        f"Body: {body}\n\n"
        "Respond with ONLY the category name."
    )

    category = call_llm(prompt).strip()

    # Safety net (LLMs can be creative when bored)
    allowed = {"Primary", "Promotions", "Social", "Spam", "Updates"}
    return category if category in allowed else "Primary"
