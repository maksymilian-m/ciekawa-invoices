import logging
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.dirname(__file__))

from src.infrastructure.firestore_adapter import FirestoreAdapter, firestore
from src.domain.entities import ProcessingStatus, SyncStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_pipeline():
    logger.info("Initializing Firestore Adapter...")
    adapter = FirestoreAdapter()
    
    # 1. Reset Sync Status for PROCESSED invoices (so they re-export to Sheets)
    logger.info("Resetting PROCESSED invoices to NOT_SYNCED...")
    processed_docs = adapter.client.collection("processed_invoices").stream()
    
    synced_reset_count = 0
    for doc in processed_docs:
        data = doc.to_dict()
        if data.get('sync_status') == SyncStatus.SYNCED.value:
            adapter.update_processed_invoice_sync_status(data['id'], SyncStatus.NOT_SYNCED.value)
            synced_reset_count += 1
            
    logger.info(f"Reset {synced_reset_count} invoices to NOT_SYNCED.")

    # 2. Reset FAILED/RETRY invoices to RETRY (so they re-process)
    logger.info("Resetting FAILED/RETRY invoices to RETRY...")
    raw_docs = adapter.client.collection("raw_invoices").stream()
    
    retry_reset_count = 0
    for doc in raw_docs:
        data = doc.to_dict()
        status = data.get('status')
        if status in [ProcessingStatus.FAILED.value, ProcessingStatus.RETRY.value, "FAILED", "RETRY"]: # Handle string or enum
             adapter.update_raw_invoice_status(data['id'], ProcessingStatus.RETRY.value)
             retry_reset_count += 1
             
    logger.info(f"Reset {retry_reset_count} invoices to RETRY.")

if __name__ == "__main__":
    reset_pipeline()
