import logging
from src.ports.interfaces import NotificationProvider

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, notification_provider: NotificationProvider):
        self.notification_provider = notification_provider

    def send_workflow_summary(self, retrieved_count: int, processed_count: int, failed_count: int, synced_count: int):
        summary = {
            "retrieved": retrieved_count,
            "processed": processed_count,
            "failed": failed_count,
            "synced": synced_count
        }
        try:
            self.notification_provider.send_summary(summary)
            logger.info("Summary email sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send summary email: {e}")
    
    def send_summary(self, summary: dict):
        """Send a custom summary dict."""
        try:
            self.notification_provider.send_summary(summary)
            logger.info("Summary email sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send summary email: {e}")
