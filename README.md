# Ciekawa Invoices - Automated Invoice Processing Agent

> Intelligent invoice processing system for Ciekawa restaurant, automating email retrieval, PDF extraction, and data export to Google Sheets.

## 🎯 Executive Summary

This system automates the complete invoice processing workflow for Ciekawa restaurant:

1. **📧 Email Retrieval**: Automatically fetches unread emails with PDF attachments from Gmail
2. **🤖 AI Extraction**: Uses Google Gemini Flash to extract structured data from invoice PDFs
3. **💾 Data Storage**: Stores raw and processed invoices in Firestore (or local JSON for testing)
4. **📊 Export**: Syncs processed invoices to Google Sheets for accounting
5. **📬 Notifications**: Sends daily summary emails to stakeholders
6. **🛡️ Duplicate Detection**: Prevents processing the same invoice multiple times

**Key Benefits:**
- ⏱️ Saves hours of manual data entry per week
- ✅ Reduces human error in invoice processing
- 📈 Provides real-time visibility into invoice status
- 🔄 Fully automated daily workflow via Cloud Run Jobs

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── domain/          # Core business entities (Invoice, Email)
├── ports/           # Abstract interfaces (Repository, Provider)
├── services/        # Business logic (Retrieval, Processing, Sync)
└── infrastructure/  # External integrations (Gmail, Gemini, Firestore, Sheets)
```

**Design Principles:**
- 🎯 **SOLID**: Single responsibility, dependency inversion
- 🧪 **TDD**: Comprehensive unit tests
- 🐍 **Modern Python**: Type hints, dataclasses, Python 3.13+
- 🔌 **Dependency Injection**: Easy to test and swap implementations

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## ✨ Features

### Core Workflow
- **Gmail Integration**: OAuth2 authentication, automatic email retrieval
- **PDF Processing**: Gemini Flash 2.5 Lite for intelligent data extraction
- **Structured Data**: Extracts vendor, date, amounts, invoice number, category
- **Firestore Storage**: Scalable cloud database for invoice records
- **Google Sheets Export**: Automated sync to accounting spreadsheet
- **Email Notifications**: Daily summary reports to multiple recipients

### Advanced Features
- **🔄 Retry Logic**: Automatic retry for LLM 429 errors (up to 5 attempts with exponential backoff)
- **🛡️ Duplicate Detection**: Prevents duplicate invoices by invoice number
- **📧 Multi-Recipient Notifications**: Send summaries to entire team
- **📅 Robust Date Parsing**: Handles multiple date formats (YYYY-MM-DD, DD.MM.YYYY, etc.)
- **⚠️ Error Handling**: Graceful failure handling with detailed error messages
- **📝 Audit Trail**: Complete processing history with timestamps and status

### Configuration
- **Flexible Categories**: Configurable invoice categories via YAML
- **Custom Prompts**: Externalized LLM instructions for easy updates
- **Environment-Based**: All credentials and settings via `.env` file

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **uv** package manager ([installation](https://github.com/astral-sh/uv))
- **Google Cloud Project** with enabled APIs:
  - Gmail API
  - Firestore API (Native mode)
  - Vertex AI API / Gemini API
  - Google Sheets API

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repo_url>
   cd ciekawa-invoices
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set up Google Cloud credentials**:
   - Download `credentials.json` from GCP Console
   - Place in project root
   - First run will prompt for OAuth authorization

### Configuration

Edit `.env` file:

```bash
# GCP Settings
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=your-location

# Gemini API
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=your-model

# Gmail
GMAIL_CREDENTIALS_PATH=credentials.json

# Firestore
FIRESTORE_DATABASE=(default)

# Google Sheets
GOOGLE_SHEETS_ID=your-spreadsheet-id

# Notifications (comma-separated for multiple recipients)
NOTIFICATION_EMAIL=manager@example.com,accountant@example.com
```

## 📖 Usage

### Run Complete Workflow

```bash
uv run ciekawa-invoices
```

This executes the full pipeline:
1. Retrieves emails with PDF attachments
2. Processes invoices with Gemini
3. Syncs to Google Sheets
4. Sends summary notification

### Run Individual Services

```bash
# Test Gmail retrieval
uv run python test_gmail_retrieval.py

# Test sample workflow with local PDFs
uv run python test_sample_workflow.py
```

### Testing

```bash
# Run all tests
uv run pytest -v

# Run specific test suite
uv run pytest tests/unit/test_processing_service.py -v
```

**Test Coverage**: Tests covering:
- Gmail adapter edge cases
- Processing service with retry logic
- Retrieval service
- Workflow integration

## 📊 Data Flow

```
┌─────────────┐
│   Gmail     │ Unread emails with PDF attachments
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ RetrievalService│ Downloads PDFs, saves RawInvoice
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ProcessingService │ Extracts data with Gemini
│  (with retry)    │ Checks for duplicates
└──────┬───────────┘
       │
       ▼
┌─────────────────┐
│  SheetsService  │ Exports to Google Sheets
└──────┬──────────┘
       │
       ▼
┌──────────────────────┐
│ NotificationService  │ Sends summary email
└──────────────────────┘
```

## 🗂️ Project Structure

```
ciekawa-invoices/
├── src/
│   ├── domain/
│   │   ├── entities.py           # Core data models
│   │   └── invoice_schema.py     # Pydantic schema for LLM
│   ├── ports/
│   │   └── interfaces.py         # Abstract interfaces
│   ├── services/
│   │   ├── retrieval_service.py  # Email retrieval logic
│   │   ├── processing_service.py # Invoice processing with retry
│   │   ├── sheets_service.py     # Google Sheets sync
│   │   └── notification_service.py # Email notifications
│   ├── infrastructure/
│   │   ├── gmail_adapter.py      # Gmail API integration
│   │   ├── gemini_adapter.py     # Gemini LLM integration
│   │   ├── firestore_adapter.py  # Firestore database
│   │   ├── json_repository.py    # Local JSON storage (testing)
│   │   ├── sheets_adapter.py     # Google Sheets API
│   │   └── email_notification_adapter.py # Email sending
│   ├── config.py                 # Configuration management
│   └── main.py                   # Main workflow orchestrator
├── tests/
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── config/
│   └── categories.yaml           # Invoice categories
├── prompts/
│   └── invoice_extraction_instruction.md # LLM prompt
├── docs/                         # Documentation
├── sample_data/                  # Sample invoices for testing
└── data/                         # Local data storage
```

## 🧪 Testing Documentation

- [Testing Gmail Integration](docs/testing_gmail.md)
- [Testing Firestore](docs/testing_firestore.md)
- [Testing Google Sheets](docs/testing_sheets.md)
- [Testing Notifications](docs/testing_notification.md)
- [Testing Sample Data](docs/testing_sample_data.md)

## 🚢 Deployment

Deploy to Google Cloud Run Jobs for automated daily execution:

```bash
# Build Docker image
docker build -t gcr.io/your-project/ciekawa-invoices .

# Push to Container Registry
docker push gcr.io/your-project/ciekawa-invoices

# Deploy to Cloud Run Jobs
gcloud run jobs create ciekawa-invoices \
  --image gcr.io/your-project/ciekawa-invoices \
  --region us-central1 \
  --schedule "0 9 * * *"  # Daily at 9 AM
```

See [docs/deployment.md](docs/deployment.md) for detailed deployment instructions.

## 🔧 Development

### Code Style

- **Type Hints**: Modern Python 3.13+ syntax (`list[str]`, `str | None`)
- **Dataclasses**: Use `@dataclass` with `slots=True` for performance
- **Docstrings**: Google-style docstrings for all public methods
- **Testing**: TDD approach, pytest for all tests

### Adding New Features

1. Update domain entities if needed (`src/domain/entities.py`)
2. Define interface in `src/ports/interfaces.py`
3. Implement in `src/infrastructure/`
4. Add business logic in `src/services/`
5. Write tests in `tests/unit/`
6. Update documentation

---

**Built with ❤️ for Ciekawa Restaurant**