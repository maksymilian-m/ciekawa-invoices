import logging
from typing import List
from datetime import datetime
from dataclasses import asdict
from google.cloud import firestore
from src.ports.interfaces import InvoiceRepository
from src.domain.entities import RawInvoice, ProcessedInvoice, ProcessingStatus, SyncStatus, Email, InvoiceData, InvoiceItem
from src.config import settings

logger = logging.getLogger(__name__)

class FirestoreAdapter(InvoiceRepository):
    def __init__(self, project_id: str | None = None, database: str | None = None):
        self.project_id = project_id or settings.gcp_project_id
        self.database = database or settings.firestore_database
        
        if not self.project_id:
            logger.warning("No GCP Project ID provided. FirestoreAdapter will fail if used.")
            self.client = None
        else:
            try:
                self.client = firestore.Client(project=self.project_id, database=self.database)
                logger.info(f"Initialized FirestoreAdapter for project {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}")
                self.client = None

    def _check_client(self):
        if not self.client:
            raise RuntimeError("Firestore client is not initialized.")

    def save_raw_invoice(self, invoice: RawInvoice):
        self._check_client()
        doc_ref = self.client.collection("raw_invoices").document(invoice.id)
        
        # Convert to dict and handle datetime
        data = asdict(invoice)
        # Firestore handles datetime objects natively, but enums need conversion
        data['status'] = invoice.status.value
        data['email_data']['date'] = invoice.email_data.date # Ensure it's datetime
        
        doc_ref.set(data)
        logger.info(f"Saved raw invoice {invoice.id} to Firestore.")

    def get_pending_raw_invoices(self) -> List[RawInvoice]:
        self._check_client()
        docs = self.client.collection("raw_invoices").where(
            filter=firestore.FieldFilter("status", "==", ProcessingStatus.PENDING.value)
        ).stream()
        
        pending = []
        for doc in docs:
            data = doc.to_dict()
            # Reconstruct objects
            email_data = data['email_data']
            email = Email(**email_data)
            
            raw = RawInvoice(
                id=data['id'],
                email_id=data['email_id'],
                email_data=email,
                status=ProcessingStatus(data['status']),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                error_message=data.get('error_message')
            )
            pending.append(raw)
        return pending

    def update_raw_invoice_status(self, invoice_id: str, status: str, error: str | None = None):
        self._check_client()
        doc_ref = self.client.collection("raw_invoices").document(invoice_id)
        
        update_data = {
            "status": status,
            "updated_at": datetime.now()
        }
        if error:
            update_data["error_message"] = error
            
        doc_ref.update(update_data)
        logger.info(f"Updated raw invoice {invoice_id} status to {status}.")

    def save_processed_invoice(self, invoice: ProcessedInvoice):
        self._check_client()
        doc_ref = self.client.collection("processed_invoices").document(invoice.id)
        
        data = asdict(invoice)
        data['sync_status'] = invoice.sync_status.value
        
        doc_ref.set(data)
        logger.info(f"Saved processed invoice {invoice.id} to Firestore.")

    def get_unsynced_processed_invoices(self) -> List[ProcessedInvoice]:
        self._check_client()
        docs = self.client.collection("processed_invoices").where(
            filter=firestore.FieldFilter("sync_status", "==", SyncStatus.NOT_SYNCED.value)
        ).stream()
        
        unsynced = []
        for doc in docs:
            data = doc.to_dict()
            inv_data = data['extracted_data']
            
            # Reconstruct nested objects
            items = [InvoiceItem(**i) for i in inv_data.get('items', [])] if inv_data.get('items') else None
            invoice_data = InvoiceData(
                invoice_date=inv_data['invoice_date'],
                category=inv_data['category'],
                vendor_name=inv_data['vendor_name'],
                net_amount=inv_data['net_amount'],
                gross_amount=inv_data['gross_amount'],
                invoice_number=inv_data['invoice_number'],
                due_date=inv_data['due_date'],
                items=items,
                currency=inv_data.get('currency', 'PLN'),
                tax_amount=inv_data.get('tax_amount', 0.0)
            )
            
            processed = ProcessedInvoice(
                id=data['id'],
                raw_invoice_id=data['raw_invoice_id'],
                extracted_data=invoice_data,
                sync_status=SyncStatus(data['sync_status']),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                error_message=data.get('error_message')
            )
            unsynced.append(processed)
        return unsynced

    def update_processed_invoice_sync_status(self, invoice_id: str, status: str, error: str | None = None):
        self._check_client()
        doc_ref = self.client.collection("processed_invoices").document(invoice_id)
        
        update_data = {
            "sync_status": status,
            "updated_at": datetime.now()
        }
        if error:
            update_data["error_message"] = error
            
        doc_ref.update(update_data)
        logger.info(f"Updated processed invoice {invoice_id} sync status to {status}.")
