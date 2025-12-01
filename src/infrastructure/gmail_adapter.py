import json
import logging
import os.path
import base64
from datetime import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.ports.interfaces import EmailProvider, FileStorage
from src.infrastructure.storage import LocalFileStorage
from src.domain.entities import Email
from src.config import settings

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailAdapter(EmailProvider):
    def __init__(self, credentials_path: str | None = None, token_path: str = "token.json", download_dir: str = "data/raw_pdfs", storage: FileStorage | None = None):
        self.credentials_path = credentials_path or settings.gmail_credentials_path
        self.token_path = token_path
        self.storage = storage or LocalFileStorage(base_dir=download_dir)
        self.service = self._authenticate()
        logger.info("Initialized GmailAdapter")

    def _authenticate(self):
        creds = None
        
        # 1. Try loading from Environment Variable (Cloud/Production)
        if settings.gmail_token_json:
            try:
                info = json.loads(settings.gmail_token_json)
                creds = Credentials.from_authorized_user_info(info, SCOPES)
                logger.info("Loaded Gmail credentials from environment variable.")
            except Exception as e:
                logger.error(f"Failed to load credentials from environment variable: {e}")

        # 2. Try loading from local file (Development)
        if not creds and os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # 3. Refresh or Login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # If we are using a file, update it
                    if os.path.exists(self.token_path):
                        with open(self.token_path, "w") as token:
                            token.write(creds.to_json())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}. Re-authenticating...")
                    creds = None
            
            # 4. Interactive Login (Local only)
            if not creds:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    logger.warning("No credentials found. GmailAdapter will not work.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())
        
        return build("gmail", "v1", credentials=creds)

    def fetch_unread_emails_with_attachments(self) -> list[Email]:
        if not self.service:
            logger.warning("Gmail service not initialized. Returning empty list.")
            return []

        try:
            # Call the Gmail API
            results = self.service.users().messages().list(userId='me', q='is:unread has:attachment').execute()
            messages = results.get('messages', [])
            
            emails = []
            if not messages:
                logger.info("No unread messages found.")
                return []

            logger.info(f"Found {len(messages)} unread messages with attachments.")
            
            for msg in messages:
                email_data = self._process_message(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def _process_message(self, msg_id: str) -> Email | None:
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()
            payload = message['payload']
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), "")
            
            # Parse date (simplified, might need robust parsing)
            try:
                email_date = datetime.strptime(date_str.split(',')[1].strip().split(' +')[0].split(' -')[0], "%d %b %Y %H:%M:%S")
            except Exception:
                email_date = datetime.now() # Fallback

            parts = payload.get('parts', [])
            
            # Find PDF attachment
            for part in parts:
                if part.get('filename') and part['filename'].lower().endswith('.pdf'):
                    filename = part['filename']
                    attachment_id = part['body'].get('attachmentId')
                    
                    if attachment_id:
                        attachment = self.service.users().messages().attachments().get(
                            userId='me', messageId=msg_id, id=attachment_id
                        ).execute()
                        
                        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        
                        # Save to storage
                        safe_filename = f"{msg_id}_{filename}"
                        file_path_str = self.storage.save_file(safe_filename, data)
                        
                        logger.info(f"Downloaded attachment: {safe_filename}")
                        
                        return Email(
                            id=msg_id,
                            sender=sender,
                            subject=subject,
                            date=email_date,
                            attachment_path=file_path_str,
                            content=message.get('snippet', "")
                        )
            
            logger.info(f"No PDF attachment found in message {msg_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to process message {msg_id}: {e}")
            return None

    def mark_as_processed(self, email_id: str):
        if not self.service:
            return
            
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {email_id} as processed (removed UNREAD label).")
        except HttpError as error:
            logger.error(f"An error occurred marking email as processed: {error}")
