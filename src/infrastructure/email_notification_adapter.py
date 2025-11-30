import logging
import os.path
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.ports.interfaces import NotificationProvider
from src.config import settings

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailNotificationAdapter(NotificationProvider):
    def __init__(self, credentials_path: str | None = None, token_path: str = "token.json", recipient_email: str | list[str] | None = None):
        self.credentials_path = credentials_path or settings.gmail_credentials_path
        self.token_path = token_path
        
        # Support both single email and list of emails
        if recipient_email is None:
            self.recipient_emails = settings.get_notification_emails()
        elif isinstance(recipient_email, str):
            self.recipient_emails = [recipient_email]
        else:
            self.recipient_emails = recipient_email
            
        self.service = self._authenticate()
        logger.info(f"Initialized EmailNotificationAdapter for {len(self.recipient_emails)} recipient(s)")

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}. Re-authenticating...")
                    creds = None
            
            if not creds:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    logger.warning("No credentials found. EmailNotificationAdapter will not work.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
        
        return build("gmail", "v1", credentials=creds)

    def send_summary(self, summary: dict):
        if not self.service:
            logger.warning("Gmail service not initialized. Skipping email.")
            return

        try:
            message_text = self._format_summary(summary)
            
            # Send to all recipients
            for recipient in self.recipient_emails:
                message = MIMEText(message_text)
                message['to'] = recipient
                message['subject'] = f"Ciekawa Invoices Summary - {summary.get('date', 'Today')}"
                
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                body = {'raw': raw_message}
                
                self.service.users().messages().send(userId='me', body=body).execute()
                logger.info(f"Sent summary email to {recipient}")

        except HttpError as error:
            logger.error(f"An error occurred sending email: {error}")
    
    def _format_summary(self, summary: dict) -> str:
        lines = [f"Invoice Processing Summary for {summary.get('date', 'Today')}", ""]
        lines.append(f"Total Processed: {summary.get('total_processed', 0)}")
        lines.append(f"Successful: {summary.get('successful', 0)}")
        lines.append(f"Failed: {summary.get('failed', 0)}")
        lines.append("")
        
        if summary.get('failures'):
            lines.append("Failures:")
            for failure in summary['failures']:
                lines.append(f"- {failure}")
        
        return "\n".join(lines)
