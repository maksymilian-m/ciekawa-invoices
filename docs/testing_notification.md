# Testing Email Notification

## Prerequisites

1.  **Google Cloud Project**: Same project as for Gmail/Firestore.
2.  **Enable Gmail API**: Already enabled for `GmailAdapter`.
3.  **Credentials**: Uses the same `credentials.json`.
4.  **Scopes**: Requires `https://www.googleapis.com/auth/gmail.send`.
    *   **IMPORTANT**: You MUST delete `token.json` and re-authenticate to grant this new scope!

## Configuration

Add to your `.env`:
```bash
NOTIFICATION_EMAIL=your-email@example.com
```

## Running Tests

Create a test script `test_notification.py`:

```python
from src.infrastructure.email_notification_adapter import EmailNotificationAdapter
from datetime import datetime

def test_notification():
    adapter = EmailNotificationAdapter()
    
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_processed": 5,
        "successful": 4,
        "failed": 1,
        "failures": ["Invoice 123: Invalid date format"]
    }
    
    adapter.send_summary(summary)
    print("Check your inbox!")

if __name__ == "__main__":
    test_notification()
```
