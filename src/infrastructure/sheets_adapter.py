import logging
from src.ports.interfaces import SheetsProvider
from src.domain.entities import ProcessedInvoice

logger = logging.getLogger(__name__)

class GoogleSheetsAdapter(SheetsProvider):
    def __init__(self, spreadsheet_id: str | None = None):
        self.spreadsheet_id = spreadsheet_id
        # TODO: Initialize Sheets API client
        logger.info("Initialized GoogleSheetsAdapter (Mock Mode)")

    def append_invoice(self, invoice: ProcessedInvoice):
        # TODO: Append row to sheet
        logger.info(f"Appending invoice {invoice.id} to Sheets (Mock).")
