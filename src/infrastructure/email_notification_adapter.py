import logging
from src.ports.interfaces import NotificationProvider

logger = logging.getLogger(__name__)

class EmailNotificationAdapter(NotificationProvider):
    def __init__(self, sender_email: str | None = None):
        self.sender_email = sender_email
        logger.info("Initialized EmailNotificationAdapter (Mock Mode)")

    def send_summary(self, summary: dict):
        # TODO: Send email via SMTP or Gmail API
        logger.info(f"Sending summary email: {summary} (Mock).")
