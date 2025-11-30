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

@dataclass(slots=True)
class Email:
    """
    Represents an email message containing an invoice.

    Attributes:
        id: Unique identifier for the email.
        sender: The sender's email address.
        subject: The subject line of the email.
        date: The date and time the email was received.
        attachment_path: File system path to the saved PDF attachment.
        content: The body content of the email (optional).
    """
    id: str
    sender: str
    subject: str
    date: datetime
    attachment_path: str  # Path to the saved PDF
    content: str | None = None # Email body content if needed

@dataclass(slots=True)
class InvoiceItem:
    """
    Represents a single line item on an invoice.

    Attributes:
        description: Description of the item.
        quantity: Quantity of the item.
        unit_price: Price per unit.
        total_price: Total price for the line item.
    """
    description: str
    quantity: float
    unit_price: float
    total_price: float

@dataclass(slots=True)
class InvoiceData:
    """
    Represents the extracted data from an invoice.

    Attributes:
        invoice_date: The date of the invoice.
        category: The category of the expense.
        vendor_name: The name of the vendor.
        net_amount: The net amount (before tax).
        gross_amount: The gross amount (after tax).
        invoice_number: The invoice number.
        due_date: The due date for payment.
        items: List of line items on the invoice (optional).
        currency: The currency code (default: PLN).
        tax_amount: The tax amount (optional).
    """
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

@dataclass(slots=True)
class RawInvoice:
    """
    Represents a raw invoice in the system, linked to an email.

    Attributes:
        id: Unique identifier for the raw invoice (UUID).
        email_id: ID of the associated email.
        email_data: The full email object.
        status: Current processing status.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
        error_message: Error message if processing failed (optional).
    """
    id: str # UUID
    email_id: str
    email_data: Email
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None

@dataclass(slots=True)
class ProcessedInvoice:
    """
    Represents a processed invoice with extracted data.

    Attributes:
        id: Unique identifier for the processed invoice (UUID).
        raw_invoice_id: ID of the source raw invoice.
        extracted_data: The structured data extracted from the invoice.
        sync_status: Current synchronization status with external systems.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
        error_message: Error message if sync failed (optional).
    """
    id: str # UUID
    raw_invoice_id: str
    extracted_data: InvoiceData
    sync_status: SyncStatus
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
