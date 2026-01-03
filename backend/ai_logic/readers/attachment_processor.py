import os
from ai_logic.readers.pdf_reader import extract_text_from_pdf
from ai_logic.readers.word_reader import extract_text_from_docx
from ai_logic.readers.excel_reader import extract_text_from_xlsx
from ai_logic.readers.csv_reader import extract_text_from_csv
from ai_logic.readers.image_reader import extract_text_from_image


def process_attachment(file_path, filename):
    """
    Process an attachment and extract text based on file type
    
    Returns:
        dict with 'filename', 'type', and 'content'
    """
    
    extension = os.path.splitext(filename)[1].lower()
    
    try:
        if extension == '.pdf':
            content = extract_text_from_pdf(file_path)
            # Limit PDF content to first 1500 chars
            content = content[:1500] if len(content) > 1500 else content
            return {
                "filename": filename,
                "type": "PDF",
                "content": content,
                "truncated": len(extract_text_from_pdf(file_path)) > 1500
            }
        
        elif extension == '.docx':
            content = extract_text_from_docx(file_path)
            # Limit Word content
            content = content[:1500] if len(content) > 1500 else content
            return {
                "filename": filename,
                "type": "Word Document",
                "content": content,
                "truncated": len(extract_text_from_docx(file_path)) > 1500
            }
        
        elif extension == '.xlsx':
            content = extract_text_from_xlsx(file_path, max_rows=20)  # Reduced rows
            return {
                "filename": filename,
                "type": "Excel Spreadsheet",
                "content": content,
                "truncated": False
            }
        
        elif extension == '.csv':
            content = extract_text_from_csv(file_path, max_rows=20)  # Reduced rows
            return {
                "filename": filename,
                "type": "CSV File",
                "content": content,
                "truncated": False
            }
        
        elif extension in ['.png', '.jpg', '.jpeg']:
            content = extract_text_from_image(file_path)
            # Limit image OCR content
            content = content[:1000] if len(content) > 1000 else content
            return {
                "filename": filename,
                "type": "Image",
                "content": content,
                "truncated": len(extract_text_from_image(file_path)) > 1000
            }
        
        else:
            return {
                "filename": filename,
                "type": "Unsupported",
                "content": f"File type {extension} not supported",
                "truncated": False
            }
    
    except Exception as e:
        return {
            "filename": filename,
            "type": "Error",
            "content": f"Error processing file: {str(e)}",
            "truncated": False
        }


def process_all_attachments(attachments):
    """
    Process multiple attachments and return their contents
    """
    processed = []
    
    for attachment in attachments:
        result = process_attachment(
            attachment['path'],
            attachment['filename']
        )
        processed.append(result)
    
    return processed


def create_attachment_summary(processed_attachments):
    """
    Create a concise summary of all attachments for the LLM
    """
    if not processed_attachments:
        return ""
    
    summary_parts = ["\n\n=== ATTACHMENTS ==="]
    
    for idx, att in enumerate(processed_attachments, 1):
        if att['content'] and not att['content'].startswith('Error') and not att['content'].startswith('File type'):
            summary_parts.append(f"\n--- Attachment {idx}: {att['filename']} ({att['type']}) ---")
            summary_parts.append(att['content'])
            if att.get('truncated'):
                summary_parts.append("[Content truncated for brevity]")
        else:
            # Just mention the attachment exists even if we can't read it
            summary_parts.append(f"\n--- Attachment {idx}: {att['filename']} ({att['type']}) ---")
            summary_parts.append(f"[Could not extract content: {att['content']}]")
    
    return "\n".join(summary_parts)


def cleanup_attachments(attachments):
    """
    Delete temporary attachment files
    """
    for attachment in attachments:
        try:
            if os.path.exists(attachment['path']):
                os.remove(attachment['path'])
        except Exception as e:
            print(f"Error cleaning up {attachment['filename']}: {str(e)}")
    
    # Clean up temp directory if empty
    try:
        temp_dir = "temp_attachments"
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temp directory: {str(e)}")