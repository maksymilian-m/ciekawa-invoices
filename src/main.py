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
from src.infrastructure.storage import LocalFileStorage, GCSFileStorage
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Ciekawa Invoices Agentic Workflow")

    # Initialize Adapters
    
    # Storage Selection
    if settings.gcs_bucket_name:
        logger.info(f"Using GCS Storage with bucket: {settings.gcs_bucket_name}")
        storage = GCSFileStorage(bucket_name=settings.gcs_bucket_name)
    else:
        logger.info("Using Local File Storage")
        storage = LocalFileStorage()

    email_provider = GmailAdapter(storage=storage)
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
    retrieval_stats = retrieval_service.run()

    # 2. Processing Phase
    logger.info("--- Phase 2: Processing ---")
    processing_stats = processing_service.run()

    # 3. Export Phase
    logger.info("--- Phase 3: Export to Sheets ---")
    sheets_stats = sheets_service.run()

    # 4. Notification Phase
    logger.info("--- Phase 4: Notification ---")
    
    retrieved_count = retrieval_stats.get('total', 0)
    processed_count = processing_stats.get('success', 0)
    processing_failed = processing_stats.get('failed', 0)
    sheets_failed = sheets_stats.get('failed', 0)
    total_failed = processing_failed + sheets_failed
    synced_count = sheets_stats.get('success', 0)
    retried_count = processing_stats.get('retried', 0)
    
    notification_service.send_workflow_summary(
        retrieved_count=retrieved_count,
        processed_count=processed_count,
        failed_count=total_failed, 
        synced_count=synced_count,
        retried_count=retried_count
    )

    logger.info("Workflow completed successfully.")

if __name__ == "__main__":
    main()
