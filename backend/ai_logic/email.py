def clean_summary(text: str) -> str:
    bad_starts = [
        "here's a summary",
        "here is a summary",
        "here's the summary",
        "here is the summary",
    ]

    lower = text.lower()
    for phrase in bad_starts:
        if lower.startswith(phrase):
            return text.split("\n", 1)[-1].strip()

    return text.strip()


def summarize_email_logic(body: str, sender: str) -> str:
    # Replace this with your LLM call later
    summary = f"The email is from {sender}. {body[:300]}..."
    return clean_summary(summary)
