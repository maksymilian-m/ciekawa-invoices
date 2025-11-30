# Deployment Guide - Ciekawa Invoices

## Overview
This guide details how to deploy the **Ciekawa Invoices** agent to **Google Cloud Platform (GCP)** using **Cloud Run Jobs**.

## Why Cloud Run Jobs?
- **Cost-Effective**: You only pay when the job is running. For a daily batch process, this is nearly free.
- **Serverless**: No servers to manage.
- **Scalable**: Can handle increased load automatically (though not needed for this use case).

## Prerequisites
1.  **GCP Project**: A Google Cloud Project with billing enabled.
2.  **APIs Enabled**:
    -   Artifact Registry API
    -   Cloud Run Admin API
    -   Cloud Build API
    -   Vertex AI API
    -   Firestore API
    -   Gmail API
    -   Google Sheets API
3.  **gcloud CLI**: Installed and authenticated.

## Cost Estimates (1000 Invoices/Month)
-   **Compute (Cloud Run)**: ~$0.00 (within Free Tier).
-   **Model (Gemini 2.5 Flash Lite)**: ~$0.10 (Extremely cost-effective). *Note: This is the recommended model for high-volume, low-cost extraction.*
-   **Storage (GCS)**: ~$0.04/month for 2GB of PDFs.
    -   *Tip*: Configure a **Lifecycle Rule** on the GCS bucket to automatically delete files after 30 days to keep costs zero.
-   **Database (Firestore)**: ~$0.00 (within Free Tier).

## Deployment Steps

### 1. Containerize the Application
Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY src ./src
COPY config ./config

# Set entrypoint
CMD ["uv", "run", "src/main.py"]
```

### 2. Build and Push Image
```bash
# Set variables
export PROJECT_ID="your-project-id"
export REGION="europe-central2" # Warsaw
export REPO_NAME="ciekawa-repo"
export IMAGE_NAME="ciekawa-invoices"

# Create Artifact Registry repo (one time)
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION

# Submit build
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest .
```

### 3. Create Cloud Run Job
```bash
gcloud run jobs create ciekawa-job \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest \
    --region $REGION \
    --set-env-vars GCP_PROJECT_ID=$PROJECT_ID \
    --service-account your-service-account@$PROJECT_ID.iam.gserviceaccount.com
```

### 4. Schedule the Job (Daily)
Use Cloud Scheduler to run the job once per day (e.g., at 2:00 AM).

```bash
gcloud scheduler jobs create http ciekawa-daily-run \
    --location $REGION \
    --schedule "0 2 * * *" \
    --uri "https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/ciekawa-job:run" \
    --http-method POST \
    --oauth-service-account-email your-scheduler-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Configuration
Ensure your application reads configuration from environment variables (using `pydantic-settings`).
