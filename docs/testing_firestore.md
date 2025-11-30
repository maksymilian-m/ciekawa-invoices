# Testing Firestore Integration

## Prerequisites

1.  **Google Cloud Project**: Ensure you have a GCP project with Firestore enabled (Native mode).
2.  **Authentication**:
    *   You need a Service Account key with `Cloud Datastore User` role.
    *   Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your key file.
    *   OR run `gcloud auth application-default login` if running locally.

## Configuration

Add to your `.env`:
```bash
GCP_PROJECT_ID=your-project-id
FIRESTORE_DATABASE=(default)
```

## Running Tests

You can create a small script to test connection:

```python
from src.infrastructure.firestore_adapter import FirestoreAdapter
from src.domain.entities import RawInvoice, ProcessingStatus, Email
from datetime import datetime
import uuid

def test_firestore():
    adapter = FirestoreAdapter()
    
    # Create dummy data
    email = Email(
        id="test_msg_1",
        sender="test@example.com",
        subject="Test Invoice",
        date=datetime.now(),
        attachment_path="/tmp/test.pdf"
    )
    
    invoice = RawInvoice(
        id=str(uuid.uuid4()),
        email_id="test_msg_1",
        email_data=email,
        status=ProcessingStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Save
    adapter.save_raw_invoice(invoice)
    print(f"Saved invoice {invoice.id}")
    
    # Retrieve
    pending = adapter.get_pending_raw_invoices()
    print(f"Found {len(pending)} pending invoices")

if __name__ == "__main__":
    test_firestore()
```
