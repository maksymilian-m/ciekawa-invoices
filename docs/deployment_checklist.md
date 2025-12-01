# GCP Deployment Checklist

This checklist ensures you've prepared everything locally before deploying to Google Cloud Platform.

## 1. Local Testing

### ✅ Gmail Retrieval
- [x] Test script created: `test_gmail_retrieval.py`
- [x] Run test and verify email retrieval works
- [x] Verify PDF download to local storage

### ✅ Firestore
- [x] Test script created: `test_firestore_connection.py`
- [ ] Run test with local emulator OR authenticated cloud project
- [ ] Verify read/write operations work

### ✅ Google Sheets
- [x] Test script created: `test_sheets_connection.py`
- [ ] Create a test spreadsheet and get its ID
- [ ] Set `GOOGLE_SHEETS_ID` in `.env`
- [ ] Run test and verify row is appended

### ✅ LLM Processing
- [x] Run `test_sample_workflow.py` to verify Gemini extraction works

## 2. GCP Setup

### Project Configuration
- [ ] Create a GCP project (or select existing)
- [ ] Enable required APIs:
  - Cloud Run API
  - Firestore API
  - Cloud Storage API
  - Secret Manager API (recommended)
- [ ] Set up billing

### Firestore Database
- [ ] Create Firestore database in Native mode
- [ ] Note the database name (default is `(default)`)

### Cloud Storage Bucket
- [ ] Create a bucket for PDF storage (e.g., `ciekawa-invoices-pdfs`)
- [ ] Set region (recommend same as Cloud Run)
- [ ] Set lifecycle rules (optional, e.g., delete after 90 days)

### Service Account
- [ ] Create a service account for the application
- [ ] Grant permissions:
  - Firestore User (for database access)
  - Storage Object Creator (for GCS uploads)
  - Secret Manager Secret Accessor (if using Secret Manager)

## 3. Credentials & Secrets

### OAuth Token (Gmail + Sheets)
**Recommended: Generate ONE token for both services**
- [ ] Run `uv run python generate_oauth_token.py`
- [ ] This creates `token.json` with both Gmail and Sheets scopes
- [ ] Copy content for both `GMAIL_TOKEN_JSON` and `GOOGLE_SHEETS_TOKEN_JSON` env vars (same value!)

**Alternative: Separate tokens** (if you prefer)
- [ ] Generate Gmail token separately
- [ ] Generate Sheets token separately in `sheets_token.json`

### Gemini API Key
- [ ] Get API key from Google AI Studio
- [ ] Prepare for `GEMINI_API_KEY` env var

### Environment Variables to Set in Cloud Run
```bash
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GCS_BUCKET_NAME=ciekawa-invoices-pdfs
GEMINI_API_KEY=your-gemini-api-key
GMAIL_TOKEN_JSON='{"token": "...", "refresh_token": "...", ...}'
GOOGLE_SHEETS_TOKEN_JSON='{"token": "...", "refresh_token": "...", ...}'  # Can be same as GMAIL_TOKEN_JSON
GOOGLE_SHEETS_ID=your-spreadsheet-id
FIRESTORE_DATABASE=(default)
NOTIFICATION_EMAIL=maksymilian.m@gmail.com
```

## 4. Docker & Deployment

### Dockerfile
- [ ] Create `Dockerfile`
- [ ] Create `.dockerignore`
- [ ] Test build locally: `docker build -t ciekawa-invoices .`

### Cloud Run Deployment
- [ ] Deploy with adequate memory (512MB minimum, 1GB recommended)
- [ ] Set timeout appropriately (5-10 minutes)
- [ ] Configure environment variables
- [ ] Set service account
- [ ] Allow unauthenticated invocations (if using Cloud Scheduler)

### Cloud Scheduler (for automation)
- [ ] Create a scheduler job
- [ ] Set frequency (e.g., daily at 8am)
- [ ] Target your Cloud Run service URL

## 5. Testing in Cloud

### Initial Deployment Test
- [ ] Deploy with a simple health check endpoint first
- [ ] Verify service starts successfully
- [ ] Check logs in Cloud Logging

### Integration Tests
- [ ] Manually trigger the service
- [ ] Verify Gmail retrieval works
- [ ] Verify Firestore writes
- [ ] Verify GCS uploads
- [ ] Verify Sheets appends
- [ ] Check for any permission errors

### Monitoring
- [ ] Set up log-based alerts for errors
- [ ] Monitor costs (especially Gemini API usage)

## 6. Common Issues & Solutions

### Authentication Failures
- **Gmail/Sheets**: Ensure token JSON is properly formatted (single line, escaped quotes)
- **Firestore**: Verify service account has correct IAM roles
- **GCS**: Check bucket permissions

### Token Expiry
- Gmail/Sheets tokens refresh automatically IF refresh_token is present
- If refresh fails, regenerate tokens locally and re-deploy

### Timeout Issues
- Increase Cloud Run timeout to 10 minutes
- Consider async processing for large batches

### File Access (GCS)
- Gemini API requires either:
  - Public URL (set bucket/object to public read)
  - Signed URL (generate with service account)
  - Local file (download from GCS first)

## 7. Security Best Practices

- [ ] Use Secret Manager for sensitive values (recommended over env vars)
- [ ] Restrict API keys to specific services
- [ ] Enable VPC connector for private resources (optional)
- [ ] Set up audit logging
- [ ] Regularly rotate OAuth tokens
