"""Test script to verify Gmail retrieval and JSON storage."""
import logging
from src.infrastructure.gmail_adapter import GmailAdapter
from src.infrastructure.json_repository import JsonInvoiceRepository
from src.services.retrieval_service import RetrievalService
from src.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gmail_retrieval():
    logger.info("Starting Gmail Retrieval Test...")
    
    # Check credentials
    if not settings.gmail_credentials_path:
        logger.error("GMAIL_CREDENTIALS_PATH not set in .env")
        logger.info("Please set GMAIL_CREDENTIALS_PATH=path/to/credentials.json")
        return

    # Initialize adapters
    email_provider = GmailAdapter()
    invoice_repo = JsonInvoiceRepository()
    
    # Initialize service
    service = RetrievalService(email_provider, invoice_repo)
    
    # Run service
    try:
        service.run()
        logger.info("Retrieval service finished successfully.")
        
        # Verify results
        pending = invoice_repo.get_pending_raw_invoices()
        logger.info(f"Current pending invoices in DB: {len(pending)}")
        for inv in pending:
            logger.info(f" - {inv.id}: {inv.email_data.subject} ({inv.email_data.attachment_path})")
            
    except Exception as e:
        logger.error(f"Retrieval service failed: {e}")

if __name__ == "__main__":
    test_gmail_retrieval()
