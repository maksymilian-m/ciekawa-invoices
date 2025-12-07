import logging
import uuid
from datetime import datetime, timezone
from src.domain.entities import RawInvoice, ProcessingStatus
from src.ports.interfaces import EmailProvider, InvoiceRepository

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, email_provider: EmailProvider, invoice_repo: InvoiceRepository):
        self.email_provider = email_provider
        self.invoice_repo = invoice_repo

    def run(self) -> dict:
        logger.info("Starting Retrieval Service...")
        emails = self.email_provider.fetch_unread_emails_with_attachments()
        logger.info(f"Found {len(emails)} emails with attachments.")

        success_count = 0
        for email in emails:
            try:
                # Create RawInvoice entity
                raw_invoice = RawInvoice(
                    id=str(uuid.uuid4()),
                    email_id=email.id,
                    email_data=email,
                    status=ProcessingStatus.PENDING,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                # Save to DB
                self.invoice_repo.save_raw_invoice(raw_invoice)
                
                # Mark email as processed in the provider (e.g. remove label)
                self.email_provider.mark_as_processed(email.id)
                
                logger.info(f"Successfully ingested email {email.id}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to process email {email.id}: {e}")
                # Note: We might want to mark it as failed in DB if we saved it, 
                # but if saving failed, we just log it. 
                # If marking as processed failed, we might re-process it next time, which is safer.
        
        return {'total': len(emails), 'success': success_count}
