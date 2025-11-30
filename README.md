# Ciekawa Invoices

Automated invoice processing agent for Ciekawa restaurant.

## Overview
This project automates the retrieval, extraction, and storage of invoices received via email. It uses Google's **Agent Development Kit (ADK)** and **Gemini Flash** to intelligently parse PDF invoices and export the data to Google Sheets.

## Architecture
This project follows **Clean Architecture**. See [docs/architecture.md](docs/architecture.md) for details.

## Prerequisites
- Python 3.13+
- `uv` package manager
- Google Cloud Project with enabled APIs:
    - Gmail API
    - Firestore API
    - Vertex AI API
    - Google Sheets API

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd ciekawa-invoices
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configuration**:
    Create a `.env` file based on `.env.example` (to be created) with your GCP credentials and settings.

## Usage

Run the main workflow:
```bash
uv run src/main.py
```

## Testing

Run unit tests:
```bash
uv run pytest tests/unit
```