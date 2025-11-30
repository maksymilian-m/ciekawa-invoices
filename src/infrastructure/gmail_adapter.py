import logging
from src.ports.interfaces import EmailProvider
from src.domain.entities import Email
from datetime import datetime

logger = logging.getLogger(__name__)

class GmailAdapter(EmailProvider):
    def __init__(self, credentials_path: str | None = None):
        self.credentials_path = credentials_path
        # TODO: Initialize Gmail API client here
        logger.info("Initialized GmailAdapter (Mock Mode)")

    def fetch_unread_emails_with_attachments(self) -> list[Email]:
        # TODO: Implement actual Gmail API call
        # 1. List messages with 'is:unread has:attachment'
        # 2. Get message details
        # 3. Download attachment
        logger.info("Fetching emails from Gmail (Mock)...")
        return []

    def mark_as_processed(self, email_id: str):
        # TODO: Remove 'UNREAD' label
        logger.info(f"Marked email {email_id} as processed (Mock).")
