# Testing Google Sheets Integration

## Prerequisites

1.  **Google Cloud Project**: Same project as for Gmail/Firestore.
2.  **Enable Sheets API**: Enable Google Sheets API in GCP Console.
3.  **Credentials**: Uses the same `credentials.json` as Gmail adapter.
4.  **Spreadsheet**:
    *   Create a new Google Sheet.
    *   Copy the Spreadsheet ID from the URL (e.g., `https://docs.google.com/spreadsheets/d/YOUR_ID_HERE/edit`).
    *   Add headers in the first row: `Data wstawienia`, `PŁATNOŚĆ ZA`, `FIRMA / KONTRAHENT`, `NETTO`, `KWOTA BRUTTO`, `NR FV`, `TERMIN PŁATNOŚCI`.

## Configuration

Add to your `.env`:
```bash
GOOGLE_SHEETS_ID=your-spreadsheet-id
```

## Running Tests

Create a test script `test_sheets.py`:

```python
from src.infrastructure.sheets_adapter import GoogleSheetsAdapter
from src.domain.entities import ProcessedInvoice, InvoiceData, SyncStatus
from datetime import datetime
import uuid

def test_sheets():
    adapter = GoogleSheetsAdapter()
    
    data = InvoiceData(
        invoice_date=datetime.now(),
        category="TEST",
        vendor_name="Test Vendor",
        net_amount=100.50,
        gross_amount=123.62,
        invoice_number="TEST/001",
        due_date=datetime.now(),
        items=[]
    )
    
    invoice = ProcessedInvoice(
        id=str(uuid.uuid4()),
        raw_invoice_id="raw_1",
        extracted_data=data,
        sync_status=SyncStatus.NOT_SYNCED,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    adapter.append_invoice(invoice)
    print("Check your spreadsheet!")

if __name__ == "__main__":
    test_sheets()
```
