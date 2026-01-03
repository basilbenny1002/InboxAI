from services.llm_client import call_llm


def summarize_email_logic(body: str, sender: str, subject: str = "", attachments: str = ""):
    """
    Summarize email body and attachments
    
    Args:
        body: Email body text
        sender: Email sender
        subject: Email subject line
        attachments: Already-processed attachment text (string)
    """
    
    print(f"\n=== Summarizing email from {sender} ===")
    print(f"Subject: {subject}")
    print(f"Body length: {len(body)} chars")
    print(f"Attachment text length: {len(attachments)} chars")
    
    # Build the prompt
    prompt_parts = []
    
    # Subject line
    if subject and subject.strip():
        prompt_parts.append(f"Subject: {subject}")
    
    # Email body
    if body and body.strip():
        body_preview = body[:1500] if len(body) > 1500 else body
        prompt_parts.append(f"\nEmail Body:\n{body_preview}")
        if len(body) > 1500:
            prompt_parts.append("[Email body truncated]")
    else:
        prompt_parts.append("\nEmail Body:\n[No body text or email may be HTML-only]")
    
    # Attachments (already processed as text)
    if attachments and attachments.strip():
        prompt_parts.append(f"\n{attachments}")
    
    # Create final prompt
    full_prompt = f"""Summarize this email from {sender} in 2-3 natural sentences. 
Be specific about the content. If there are attachments, briefly mention what they contain.

{chr(10).join(prompt_parts)}

Summary:"""
    
    print(f"Prompt length: {len(full_prompt)} chars")
    
    # Call LLM with combined content
    try:
        summary = call_llm(full_prompt)
        print(f"Summary generated successfully")
        return summary
    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        
        # Fallback summary
        if body and body.strip():
            preview = body[:100].strip()
            return f"Email from {sender} about: {preview}... [Error generating full summary]"
        else:
            return f"Email from {sender} with subject '{subject}'. [No body content available]"