import logging
import uuid
from datetime import datetime
from src.infrastructure.sheets_adapter import GoogleSheetsAdapter
from src.domain.entities import ProcessedInvoice, InvoiceData, SyncStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sheets():
    logger.info("Testing Google Sheets Connection...")
    
    try:
        adapter = GoogleSheetsAdapter()
    except Exception as e:
        logger.error(f"Failed to init adapter: {e}")
        return

    if not adapter.service:
        logger.error("Sheets service not initialized.")
        return

    # Create dummy data
    invoice_data = InvoiceData(
        invoice_date=datetime.now(),
        category="TEST_CATEGORY",
        vendor_name="Test Vendor",
        net_amount=100.00,
        gross_amount=123.00,
        invoice_number=f"TEST-{uuid.uuid4().hex[:6]}",
        due_date=datetime.now()
    )
    
    processed_invoice = ProcessedInvoice(
        id=str(uuid.uuid4()),
        raw_invoice_id="test_raw_id",
        extracted_data=invoice_data,
        sync_status=SyncStatus.NOT_SYNCED,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Test Append
    try:
        logger.info(f"Attempting to append invoice {processed_invoice.extracted_data.invoice_number}...")
        adapter.append_invoice(processed_invoice)
        logger.info("Append successful.")
    except Exception as e:
        logger.error(f"Append failed: {e}")

if __name__ == "__main__":
    test_sheets()
