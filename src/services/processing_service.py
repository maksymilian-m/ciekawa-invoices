import logging
import uuid
from datetime import datetime, timezone
from src.domain.entities import ProcessedInvoice, InvoiceData, SyncStatus, ProcessingStatus, InvoiceItem
from src.ports.interfaces import InvoiceRepository, LLMProvider

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self, invoice_repo: InvoiceRepository, llm_provider: LLMProvider):
        self.invoice_repo = invoice_repo
        self.llm_provider = llm_provider
    
    def run(self) -> dict:
        """
        Processes pending and retry invoices.
        Returns statistics: total, success, failed, retried counts.
        """
        logger.info("Starting Processing Service...")
        
        pending_invoices = self.invoice_repo.get_pending_raw_invoices([ProcessingStatus.PENDING, ProcessingStatus.RETRY])
        logger.info(f"Found {len(pending_invoices)} pending/retry invoices.")
        
        stats = {'total': len(pending_invoices), 'success': 0, 'failed': 0, 'retried': 0}

        for raw_invoice in pending_invoices:
            try:
                result_status = self._process_single_invoice(raw_invoice)
                if result_status == ProcessingStatus.PROCESSED:
                    stats['success'] += 1
                elif result_status == ProcessingStatus.RETRY:
                    stats['retried'] += 1
                else:
                    stats['failed'] += 1
            except Exception:
                stats['failed'] += 1
                
        return stats

    def _process_single_invoice(self, raw_invoice) -> ProcessingStatus:
        logger.info(f"Processing invoice {raw_invoice.id}...")
        
        try:
            # Extract data using LLM with retry logic
            extracted_dict = self._extract_with_retry(raw_invoice.email_data.attachment_path)
            
            # Validate and map data
            invoice_data = self._map_and_validate(extracted_dict)
            
            # Check for duplicate invoice number
            if self.invoice_repo.invoice_number_exists(invoice_data.invoice_number):
                logger.warning(f"Duplicate invoice detected: {invoice_data.invoice_number}")
                self.invoice_repo.update_raw_invoice_status(
                    raw_invoice.id, 
                    ProcessingStatus.FAILED.value, 
                    f"Duplicate invoice number: {invoice_data.invoice_number}"
                )
                return ProcessingStatus.FAILED

            processed_invoice = ProcessedInvoice(
                id=str(uuid.uuid4()),
                raw_invoice_id=raw_invoice.id,
                extracted_data=invoice_data,
                sync_status=SyncStatus.NOT_SYNCED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            # Save processed invoice
            self.invoice_repo.save_processed_invoice(processed_invoice)
            
            # Update raw invoice status
            self.invoice_repo.update_raw_invoice_status(raw_invoice.id, ProcessingStatus.PROCESSED.value)
            
            logger.info(f"Successfully processed invoice {raw_invoice.id}")
            return ProcessingStatus.PROCESSED

        except Exception as e:
            logger.error(f"Failed to process invoice {raw_invoice.id}: {e}")
            
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning(f"Quota exceeded for invoice {raw_invoice.id}. Marking as RETRY.")
                self.invoice_repo.update_raw_invoice_status(raw_invoice.id, ProcessingStatus.RETRY.value, str(e))
                return ProcessingStatus.RETRY
            
            self.invoice_repo.update_raw_invoice_status(raw_invoice.id, ProcessingStatus.FAILED.value, str(e))
            raise

    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, TooManyRequests

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=10, max=120),
        retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable, TooManyRequests)),
        reraise=True
    )
    def _extract_with_retry(self, file_path: str) -> dict:
        return self.llm_provider.extract_invoice_data(file_path)

    def _map_and_validate(self, data: dict) -> InvoiceData:
        try:
            # Robust date parsing with fallbacks
            def parse_date(date_str: str) -> datetime:
                for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d-%m-%Y'):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Unknown date format: {date_str}")

            return InvoiceData(
                invoice_date=parse_date(data.get('invoice_date', '')),
                category=data.get('category', 'UNCATEGORIZED'),
                vendor_name=data.get('vendor', 'Unknown'),
                net_amount=float(data.get('net_amount', 0.0)),
                gross_amount=float(data.get('gross_amount', 0.0)),
                invoice_number=data.get('invoice_number', 'UNKNOWN'),
                due_date=parse_date(data.get('payment_date', '')),
                items=[],
                currency=data.get('currency', 'PLN'),
                tax_amount=float(data.get('tax_amount', 0.0))
            )
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Data validation failed: {e}. Raw data: {data}")
            raise ValueError(f"Invalid invoice data structure: {e}")


