from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

class ProcessingStatus(Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class SyncStatus(Enum):
    NOT_SYNCED = "NOT_SYNCED"
    SYNCED = "SYNCED"
    FAILED = "FAILED"

@dataclass
class Email:
    id: str
    sender: str
    subject: str
    date: datetime
    attachment_path: str  # Path to the saved PDF
    content: Optional[str] = None # Email body content if needed

@dataclass
class InvoiceItem:
    description: str
    quantity: float
    unit_price: float
    total_price: float

@dataclass
class InvoiceData:
    vendor_name: str
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]
    total_amount: float
    currency: str
    items: List[InvoiceItem]
    tax_amount: Optional[float] = 0.0

@dataclass
class RawInvoice:
    id: str # UUID
    email_id: str
    email_data: Email
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

@dataclass
class ProcessedInvoice:
    id: str # UUID
    raw_invoice_id: str
    extracted_data: InvoiceData
    sync_status: SyncStatus
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
