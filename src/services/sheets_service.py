import logging
from src.domain.entities import SyncStatus
from src.ports.interfaces import InvoiceRepository, SheetsProvider

logger = logging.getLogger(__name__)

class SheetsService:
    def __init__(self, invoice_repo: InvoiceRepository, sheets_provider: SheetsProvider):
        self.invoice_repo = invoice_repo
        self.sheets_provider = sheets_provider

    def run(self) -> dict:
        logger.info("Starting Sheets Sync Service...")
        unsynced_invoices = self.invoice_repo.get_unsynced_processed_invoices()
        logger.info(f"Found {len(unsynced_invoices)} unsynced invoices.")

        success_count = 0
        failed_count = 0

        for invoice in unsynced_invoices:
            try:
                self.sheets_provider.append_invoice(invoice)
                self.invoice_repo.update_processed_invoice_sync_status(invoice.id, SyncStatus.SYNCED.value)
                logger.info(f"Successfully synced invoice {invoice.id} to Sheets.")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to sync invoice {invoice.id}: {e}")
                self.invoice_repo.update_processed_invoice_sync_status(invoice.id, SyncStatus.FAILED.value, str(e))
                failed_count += 1
        
        return {'total': len(unsynced_invoices), 'success': success_count, 'failed': failed_count}
