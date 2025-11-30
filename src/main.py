import logging
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.retrieval_service import RetrievalService
from src.services.processing_service import ProcessingService
from src.services.sheets_service import SheetsService
from src.services.notification_service import NotificationService

from src.infrastructure.gmail_adapter import GmailAdapter
from src.infrastructure.firestore_adapter import FirestoreAdapter
from src.infrastructure.gemini_adapter import GeminiAdapter
from src.infrastructure.sheets_adapter import GoogleSheetsAdapter
from src.infrastructure.email_notification_adapter import EmailNotificationAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Ciekawa Invoices Agentic Workflow")

    # Initialize Adapters
    # In the future, these will take config from env vars
    email_provider = GmailAdapter()
    invoice_repo = FirestoreAdapter()
    llm_provider = GeminiAdapter()
    sheets_provider = GoogleSheetsAdapter()
    notification_provider = EmailNotificationAdapter()

    # Initialize Services
    retrieval_service = RetrievalService(email_provider, invoice_repo)
    processing_service = ProcessingService(invoice_repo, llm_provider)
    sheets_service = SheetsService(invoice_repo, sheets_provider)
    notification_service = NotificationService(notification_provider)

    # 1. Retrieval Phase
    logger.info("--- Phase 1: Retrieval ---")
    retrieval_service.run()

    # 2. Processing Phase
    logger.info("--- Phase 2: Processing ---")
    processing_service.run()

    # 3. Export Phase
    logger.info("--- Phase 3: Export to Sheets ---")
    sheets_service.run()

    # 4. Notification Phase
    # Note: In a real scenario, we'd track counts from the services to pass here
    logger.info("--- Phase 4: Notification ---")
    notification_service.send_workflow_summary(0, 0, 0, 0)

    logger.info("Workflow completed successfully.")

if __name__ == "__main__":
    main()
