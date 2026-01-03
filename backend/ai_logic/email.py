from services.llm_client import call_llm
from ai_logic.readers.attachment_processor import (
    process_all_attachments, 
    cleanup_attachments,
    create_attachment_summary
)


def summarize_email_logic(body: str, sender: str, attachments=None):
    """
    Summarize email body and attachments with robust error handling
    """
    
    print(f"\n=== Summarizing email from {sender} ===")
    print(f"Body length: {len(body)} chars")
    print(f"Attachments: {len(attachments) if attachments else 0}")
    
    # Build the prompt
    prompt_parts = []
    
    # Email body
    if body and body.strip():
        body_preview = body[:1500] if len(body) > 1500 else body
        prompt_parts.append(f"Email Body:\n{body_preview}")
        if len(body) > 1500:
            prompt_parts.append("[Email body truncated]")
    else:
        prompt_parts.append("Email Body:\n[No body text]")
    
    # Process attachments if present
    if attachments and len(attachments) > 0:
        print(f"Processing {len(attachments)} attachments...")
        
        try:
            processed_attachments = process_all_attachments(attachments)
            
            # Count successful vs failed
            successful = [a for a in processed_attachments if not a['content'].startswith('[ERROR') and not a['content'].startswith('Error')]
            print(f"  Successfully processed: {len(successful)}/{len(processed_attachments)}")
            
            if successful:
                attachment_summary = create_attachment_summary(processed_attachments)
                prompt_parts.append(attachment_summary)
            else:
                prompt_parts.append(f"\n\n[{len(attachments)} attachment(s) present but could not be read]")
            
            # Cleanup temp files
            cleanup_attachments(attachments)
            
        except Exception as e:
            print(f"Error processing attachments: {str(e)}")
            prompt_parts.append(f"\n\n[Error processing {len(attachments)} attachment(s): {str(e)}]")
    
    # Create final prompt
    full_prompt = f"""Summarize this email from {sender} in 2-3 natural sentences. 
If there are attachments, briefly mention what they contain.

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
        return f"Email from {sender} about {body[:100]}... [Error generating full summary]"
