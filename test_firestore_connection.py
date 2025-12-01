import logging
import uuid
from datetime import datetime
from src.infrastructure.firestore_adapter import FirestoreAdapter
from src.domain.entities import RawInvoice, ProcessingStatus, Email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firestore():
    logger.info("Testing Firestore Connection...")
    
    # Initialize adapter
    # Note: This requires GOOGLE_APPLICATION_CREDENTIALS or gcloud auth application-default login
    try:
        adapter = FirestoreAdapter()
    except Exception as e:
        logger.error(f"Failed to init adapter: {e}")
        return

    if not adapter.client:
        logger.error("Firestore client not initialized. Check credentials.")
        return

    # Create dummy data
    invoice_id = str(uuid.uuid4())
    email = Email(
        id="test_email_id",
        sender="test@example.com",
        subject="Test Invoice",
        date=datetime.now(),
        attachment_path="/tmp/test.pdf",
        content="Test content"
    )
    
    raw_invoice = RawInvoice(
        id=invoice_id,
        email_id="test_email_id",
        email_data=email,
        status=ProcessingStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Test Save
    try:
        logger.info(f"Attempting to save invoice {invoice_id}...")
        adapter.save_raw_invoice(raw_invoice)
        logger.info("Save successful.")
    except Exception as e:
        logger.error(f"Save failed: {e}")
        return

    # Test Read
    try:
        logger.info("Attempting to read pending invoices...")
        pending = adapter.get_pending_raw_invoices()
        found = any(i.id == invoice_id for i in pending)
        if found:
            logger.info("Read successful. Found our test invoice.")
        else:
            logger.warning("Read successful but test invoice not found (might be status mismatch or delay).")
    except Exception as e:
        logger.error(f"Read failed: {e}")

    # Clean up (optional, or just leave it)
    logger.info("Firestore test finished.")

if __name__ == "__main__":
    test_firestore()
