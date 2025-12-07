import logging
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.dirname(__file__))

from src.infrastructure.firestore_adapter import FirestoreAdapter
from src.domain.entities import ProcessingStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_failed_invoices():
    logger.info("Initializing Firestore Adapter...")
    adapter = FirestoreAdapter()
    
    logger.info("Fetching FAILED invoices...")
    # Fetch FAILED invoices. Note: get_pending_raw_invoices was updated to accept a list of statuses
    failed_invoices = adapter.get_pending_raw_invoices([ProcessingStatus.FAILED])
    
    logger.info(f"Found {len(failed_invoices)} FAILED invoices.")
    
    if not failed_invoices:
        logger.info("No invoices to reset.")
        return

    logger.info("Resetting statuses to RETRY...")
    count = 0
    for invoice in failed_invoices:
        try:
            adapter.update_raw_invoice_status(invoice.id, ProcessingStatus.RETRY.value)
            count += 1
            if count % 5 == 0:
                logger.info(f"Reset {count} invoices...")
        except Exception as e:
            logger.error(f"Failed to reset invoice {invoice.id}: {e}")

    logger.info(f"Successfully reset {count} invoices to RETRY status.")

if __name__ == "__main__":
    reset_failed_invoices()
