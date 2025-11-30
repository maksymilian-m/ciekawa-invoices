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

    def run(self):
        logger.info("Starting Processing Service...")
        pending_invoices = self.invoice_repo.get_pending_raw_invoices()
        logger.info(f"Found {len(pending_invoices)} pending invoices.")

        for raw_invoice in pending_invoices:
            try:
                logger.info(f"Processing invoice {raw_invoice.id}...")
                
                # Extract data using LLM
                extracted_dict = self.llm_provider.extract_invoice_data(raw_invoice.email_data.attachment_path)
                
                # Map dict to InvoiceData dataclass
                # Note: This assumes the LLM returns a dict matching our schema. 
                # In a real app, we'd add validation here (e.g. Pydantic).
                invoice_data = self._map_to_invoice_data(extracted_dict)

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

            except Exception as e:
                logger.error(f"Failed to process invoice {raw_invoice.id}: {e}")
                self.invoice_repo.update_raw_invoice_status(raw_invoice.id, ProcessingStatus.FAILED.value, str(e))

    def _map_to_invoice_data(self, data: dict) -> InvoiceData:
        # Helper to convert dictionary to InvoiceData object
        # Handles date parsing and type conversion as needed
        items = [
            InvoiceItem(
                description=item.get('description', ''),
                quantity=float(item.get('quantity', 0)),
                unit_price=float(item.get('unit_price', 0)),
                total_price=float(item.get('total_price', 0))
            ) for item in data.get('items', [])
        ]
        
        # Simple date parsing - assumes ISO format or similar from LLM
        # In production, use a robust parser
        invoice_date = datetime.fromisoformat(data.get('invoice_date')) if data.get('invoice_date') else datetime.now()
        due_date = datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None

        return InvoiceData(
            vendor_name=data.get('vendor_name', 'Unknown'),
            invoice_number=data.get('invoice_number', ''),
            invoice_date=invoice_date,
            due_date=due_date,
            total_amount=float(data.get('total_amount', 0)),
            currency=data.get('currency', 'PLN'),
            items=items,
            tax_amount=float(data.get('tax_amount', 0))
        )
