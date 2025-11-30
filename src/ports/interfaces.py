from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import RawInvoice, ProcessedInvoice, Email

class EmailProvider(ABC):
    @abstractmethod
    def fetch_unread_emails_with_attachments(self) -> List[Email]:
        pass

    @abstractmethod
    def mark_as_processed(self, email_id: str):
        pass

class InvoiceRepository(ABC):
    @abstractmethod
    def save_raw_invoice(self, invoice: RawInvoice):
        pass

    @abstractmethod
    def get_pending_raw_invoices(self) -> List[RawInvoice]:
        pass

    @abstractmethod
    def update_raw_invoice_status(self, invoice_id: str, status: str, error: Optional[str] = None):
        pass

    @abstractmethod
    def save_processed_invoice(self, invoice: ProcessedInvoice):
        pass
    
    @abstractmethod
    def get_unsynced_processed_invoices(self) -> List[ProcessedInvoice]:
        pass

    @abstractmethod
    def update_processed_invoice_sync_status(self, invoice_id: str, status: str, error: Optional[str] = None):
        pass

class LLMProvider(ABC):
    @abstractmethod
    def extract_invoice_data(self, file_path: str) -> dict:
        pass

class SheetsProvider(ABC):
    @abstractmethod
    def append_invoice(self, invoice: ProcessedInvoice):
        pass

class NotificationProvider(ABC):
    @abstractmethod
    def send_summary(self, summary: dict):
        pass
