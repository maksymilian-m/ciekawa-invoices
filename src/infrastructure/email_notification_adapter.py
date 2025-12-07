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
            # Send to all recipients
            for recipient in self.recipient_emails:
                message = self._create_message(recipient, summary)
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                body = {'raw': raw_message}
                
                self.service.users().messages().send(userId='me', body=body).execute()
                logger.info(f"Sent summary email to {recipient}")

        except HttpError as error:
            logger.error(f"An error occurred sending email: {error}")
            
    def _create_message(self, recipient: str, summary: dict):
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime
        
        message = MIMEMultipart()
        message['to'] = recipient
        message['subject'] = f"Faktury - Podsumowanie z {datetime.now().strftime('%d.%m.%Y')}"
        
        retrieved = summary.get('retrieved', 0)
        processed = summary.get('processed', 0)
        failed = summary.get('failed', 0)
        synced = summary.get('synced', 0)
        retried = summary.get('retried', 0)
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Podsumowanie przetwarzania faktur</h2>
            <p>Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Nowe faktury pobrane z emaila:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{retrieved}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Przetworzone pomyślnie:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{processed}</td>
                </tr>
                <tr style="background-color: #e8f5e9;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Dodane do arkusza:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>{synced}</strong></td>
                </tr>
                <tr style="background-color: #fff3cd;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Oczekujące (limit API):</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{retried}</td>
                </tr>
                <tr style="background-color: #f8d7da;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Błędy:</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{failed}</td>
                </tr>
            </table>
            
            <p><a href="https://docs.google.com/spreadsheets/d/{settings.google_sheets_id}" style="color: #1a73e8; text-decoration: none;">➜ Otwórz arkusz Google Sheets</a></p>
            
            {f'<p style="color: #856404;"><em>Uwaga: {retried} faktur oczekuje na ponowne przetworzenie z powodu limitów API. Zostaną przetworzone przy następnym uruchomieniu.</em></p>' if retried > 0 else ''}
            {f'<p style="color: #721c24;"><em>Uwaga: {failed} faktur nie zostało przetworzonych. Sprawdź logi.</em></p>' if failed > 0 else ''}
        </body>
        </html>
        """
        
        message.attach(MIMEText(body_html, 'html'))
        return message
