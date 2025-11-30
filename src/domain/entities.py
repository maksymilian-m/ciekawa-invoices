from enum import Enum
from dataclasses import dataclass
from datetime import datetime

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
    content: str | None = None # Email body content if needed

@dataclass
class InvoiceItem:
    description: str
    quantity: float
    unit_price: float
    total_price: float

@dataclass
class InvoiceData:
    invoice_date: datetime
    category: str
    vendor_name: str
    net_amount: float
    gross_amount: float
    invoice_number: str
    due_date: datetime
    items: list[InvoiceItem] | None = None # Optional now, as we focus on header data
    currency: str = "PLN" # Default to PLN as per sample data context
    tax_amount: float | None = 0.0

@dataclass
class RawInvoice:
    id: str # UUID
    email_id: str
    email_data: Email
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None

@dataclass
class ProcessedInvoice:
    id: str # UUID
    raw_invoice_id: str
    extracted_data: InvoiceData
    sync_status: SyncStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
