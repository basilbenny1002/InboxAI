import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def get_unread_emails(max_results=10):
    service = get_gmail_service()
    
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    print(f"Found {len(messages)} unread messages")
    
    emails = []
    for msg in messages:
        try:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg_data['payload']['headers']
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
            print(f"Processing: {sender} - {subject}")
            
            # Extract body
            body = extract_body(msg_data['payload'])
            
            # Extract attachments (with error handling)
            attachments = []
            try:
                if 'parts' in msg_data['payload']:
                    attachments = extract_attachments(service, msg['id'], msg_data['payload']['parts'])
                    print(f"  Found {len(attachments)} attachments")
            except Exception as e:
                print(f"  Error extracting attachments: {str(e)}")
                # Continue without attachments rather than failing completely
            
            emails.append({
                "id": msg['id'],
                "sender": sender,
                "subject": subject,
                "body": body,
                "attachments": attachments
            })
            
        except Exception as e:
            print(f"Error processing message {msg['id']}: {str(e)}")
            # Continue to next email instead of failing completely
            continue
    
    print(f"Successfully processed {len(emails)} emails")
    return emails


def extract_body(payload):
    """Extract email body from payload"""
    body = ""
    
    try:
        if 'parts' in payload:
            for part in payload['parts']:
                # Handle nested parts (multipart emails)
                if 'parts' in part:
                    body = extract_body(part)
                    if body:
                        break
                
                # Look for text/plain content
                if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
                
                # Fallback to text/html if no plain text
                if not body and part['mimeType'] == 'text/html' and 'data' in part.get('body', {}):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        else:
            # Simple email without parts
            if 'data' in payload.get('body', {}):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    except Exception as e:
        print(f"Error extracting body: {str(e)}")
        body = "[Could not extract email body]"
    
    return body


def extract_attachments(service, message_id, parts):
    """Extract attachment metadata and download them"""
    attachments = []
    
    for part in parts:
        try:
            # Check for nested parts (multipart emails)
            if 'parts' in part:
                attachments.extend(extract_attachments(service, message_id, part['parts']))
                continue
            
            # Check if this part is an attachment
            filename = part.get('filename', '')
            if not filename or not part['body'].get('attachmentId'):
                continue
            
            # Only process supported file types
            supported_extensions = ['.pdf', '.docx', '.xlsx', '.csv', '.png', '.jpg', '.jpeg']
            if not any(filename.lower().endswith(ext) for ext in supported_extensions):
                print(f"  Skipping unsupported attachment: {filename}")
                continue
            
            attachment_id = part['body']['attachmentId']
            mime_type = part.get('mimeType', '')
            
            print(f"  Downloading attachment: {filename}")
            
            # Download attachment with timeout protection
            try:
                attachment = service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id
                ).execute()
                
                file_data = base64.urlsafe_b64decode(attachment['data'])
                
                # Save to temporary directory
                temp_dir = "temp_attachments"
                os.makedirs(temp_dir, exist_ok=True)
                
                # Sanitize filename
                safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
                file_path = os.path.join(temp_dir, safe_filename)
                
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                
                print(f"    Saved to: {file_path}")
                
                attachments.append({
                    "filename": filename,
                    "path": file_path,
                    "mime_type": mime_type
                })
            
            except Exception as e:
                print(f"    Error downloading {filename}: {str(e)}")
                # Continue to next attachment
                continue
        
        except Exception as e:
            print(f"  Error processing attachment part: {str(e)}")
            continue
    
    return attachments