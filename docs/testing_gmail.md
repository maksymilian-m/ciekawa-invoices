# Testing Gmail Integration

## Prerequisites

1.  **Google Cloud Project**: Ensure you have a GCP project.
2.  **Enable Gmail API**: Go to [Console](https://console.cloud.google.com/apis/library/gmail.googleapis.com) and enable Gmail API.
3.  **Create Credentials**:
    *   Go to **APIs & Services > Credentials**.
    *   Click **Create Credentials > OAuth client ID**.
    *   Application type: **Desktop app**.
    *   Name: `Ciekawa Invoices Local`.
    *   Click **Create** and download the JSON file.
    *   Save it as `credentials.json` in the project root (or anywhere you like).
4.  **Configure .env**:
    ```bash
    GMAIL_CREDENTIALS_PATH=credentials.json
    ```

## Running the Test

1.  Run the test script:
    ```bash
    uv run python test_gmail_retrieval.py
    ```
2.  **First Run**: It will open a browser window to authenticate with your Gmail account.
    *   Select your account.
    *   Allow access to view and modify emails (needed to remove 'UNREAD' label).
    *   It will create a `token.json` file for future runs.
3.  **Subsequent Runs**: It will use `token.json` automatically.

## What It Does

1.  Connects to Gmail.
2.  Searches for emails with `is:unread has:attachment`.
3.  Downloads PDF attachments to `data/raw_pdfs`.
4.  Saves metadata to `data/db/raw_invoices.json`.
5.  Marks emails as processed (removes `UNREAD` label).

## Verification

Check `data/db/raw_invoices.json` to see the ingested invoices.
