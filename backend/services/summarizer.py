def summarize_emails(llm, emails):
    if not emails:
        return "You have no unread emails."

    combined_text = ""

    for i, email in enumerate(emails, start=1):
        combined_text += f"""
Email {i}
From: {email['from']}
Subject: {email['subject']}
Body:
{email['body']}
"""

    prompt = f"""
Summarize the following unread emails.
Rules:
- Be concise
- Group similar emails
- Use bullet points
- Ignore signatures and promotions

Emails:
{combined_text}
"""

    response = llm.invoke(prompt)
    return response.content
