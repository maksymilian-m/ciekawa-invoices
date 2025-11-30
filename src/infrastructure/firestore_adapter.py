import logging
from src.ports.interfaces import InvoiceRepository
from src.domain.entities import RawInvoice, ProcessedInvoice

logger = logging.getLogger(__name__)

class FirestoreAdapter(InvoiceRepository):
    def __init__(self, project_id: str | None = None):
        self.project_id = project_id
        # TODO: Initialize Firestore client
        logger.info("Initialized FirestoreAdapter (Mock Mode)")

    def save_raw_invoice(self, invoice: RawInvoice):
        logger.info(f"Saving raw invoice {invoice.id} to Firestore (Mock).")

    def get_pending_raw_invoices(self) -> list[RawInvoice]:
        logger.info("Fetching pending raw invoices from Firestore (Mock).")
        return []

    def update_raw_invoice_status(self, invoice_id: str, status: str, error: str | None = None):
        logger.info(f"Updating raw invoice {invoice_id} status to {status} (Mock).")

    def save_processed_invoice(self, invoice: ProcessedInvoice):
        logger.info(f"Saving processed invoice {invoice.id} to Firestore (Mock).")

    def get_unsynced_processed_invoices(self) -> list[ProcessedInvoice]:
        logger.info("Fetching unsynced processed invoices from Firestore (Mock).")
        return []

    def update_processed_invoice_sync_status(self, invoice_id: str, status: str, error: str | None = None):
        logger.info(f"Updating processed invoice {invoice_id} sync status to {status} (Mock).")
