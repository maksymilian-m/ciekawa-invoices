import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from dataclasses import asdict

from src.ports.interfaces import InvoiceRepository
from src.domain.entities import RawInvoice, ProcessedInvoice, ProcessingStatus, SyncStatus, Email, InvoiceData, InvoiceItem

logger = logging.getLogger(__name__)

class JsonInvoiceRepository(InvoiceRepository):
    """Local JSON-based implementation of InvoiceRepository for testing."""
    
    def __init__(self, data_dir: str = "data/db"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.raw_invoices_file = self.data_dir / "raw_invoices.json"
        self.processed_invoices_file = self.data_dir / "processed_invoices.json"
        
        self._init_db()

    def _init_db(self):
        if not self.raw_invoices_file.exists():
            self._save_json(self.raw_invoices_file, [])
        if not self.processed_invoices_file.exists():
            self._save_json(self.processed_invoices_file, [])

    def _save_json(self, path: Path, data: list):
        # Helper to serialize datetime and enums
        def default(o):
            if isinstance(o, (datetime, datetime.date)):
                return o.isoformat()
            if isinstance(o, (ProcessingStatus, SyncStatus)):
                return o.value
            return str(o)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=default, indent=2, ensure_ascii=False)

    def _load_json(self, path: Path) -> list:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_raw_invoice(self, invoice: RawInvoice):
        data = self._load_json(self.raw_invoices_file)
        # Check if exists
        if any(i['id'] == invoice.id for i in data):
            logger.warning(f"Raw invoice {invoice.id} already exists.")
            return
        
        # Convert dataclass to dict
        invoice_dict = asdict(invoice)
        data.append(invoice_dict)
        self._save_json(self.raw_invoices_file, data)
        logger.info(f"Saved raw invoice {invoice.id} to JSON DB.")

    def get_pending_raw_invoices(self) -> List[RawInvoice]:
        data = self._load_json(self.raw_invoices_file)
        pending = []
        for item in data:
            if item['status'] == ProcessingStatus.PENDING.value:
                # Reconstruct objects
                email_data = item['email_data']
                email = Email(**email_data)
                # Fix datetime
                if isinstance(email.date, str):
                    email.date = datetime.fromisoformat(email.date)
                
                raw = RawInvoice(
                    id=item['id'],
                    email_id=item['email_id'],
                    email_data=email,
                    status=ProcessingStatus(item['status']),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at']),
                    error_message=item.get('error_message')
                )
                pending.append(raw)
        return pending

    def update_raw_invoice_status(self, invoice_id: str, status: str, error: str | None = None):
        data = self._load_json(self.raw_invoices_file)
        for item in data:
            if item['id'] == invoice_id:
                item['status'] = status
                item['updated_at'] = datetime.now().isoformat()
                if error:
                    item['error_message'] = error
                break
        self._save_json(self.raw_invoices_file, data)
        logger.info(f"Updated raw invoice {invoice_id} status to {status}.")

    def save_processed_invoice(self, invoice: ProcessedInvoice):
        data = self._load_json(self.processed_invoices_file)
        if any(i['id'] == invoice.id for i in data):
            return
        
        invoice_dict = asdict(invoice)
        data.append(invoice_dict)
        self._save_json(self.processed_invoices_file, data)
        logger.info(f"Saved processed invoice {invoice.id} to JSON DB.")

                    sync_status=SyncStatus(item['sync_status']),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at']),
                    error_message=item.get('error_message')
                )
                unsynced.append(processed)
        return unsynced

    def update_processed_invoice_sync_status(self, invoice_id: str, status: str, error: str | None = None):
        data = self._load_json(self.processed_invoices_file)
        for item in data:
            if item['id'] == invoice_id:
                item['sync_status'] = status
                item['updated_at'] = datetime.now().isoformat()
                if error:
                    item['error_message'] = error
                break
        self._save_json(self.processed_invoices_file, data)
        logger.info(f"Updated processed invoice {invoice_id} sync status to {status}.")
