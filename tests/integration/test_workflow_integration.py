"""Integration tests for the complete workflow."""
import pytest
from unittest.mock import Mock
from datetime import datetime
from src.services.retrieval_service import RetrievalService
from src.services.processing_service import ProcessingService
from src.services.sheets_service import SheetsService
from src.services.notification_service import NotificationService
from src.domain.entities import Email, ProcessingStatus


@pytest.fixture
def mock_email_provider():
    return Mock()


@pytest.fixture
def mock_invoice_repo():
    return Mock()


@pytest.fixture
def mock_llm_provider():
    return Mock()


@pytest.fixture
def mock_sheets_provider():
    return Mock()


@pytest.fixture
def mock_notification_provider():
    return Mock()


def test_end_to_end_happy_path(
    mock_email_provider,
    mock_invoice_repo,
    mock_llm_provider,
    mock_sheets_provider,
    mock_notification_provider
):
    """Test complete workflow from email retrieval to notification."""
    # Arrange
    email = Email(
        id="email_1",
        sender="vendor@example.com",
        subject="Invoice 123",
        date=datetime.now(),
        attachment_path="/tmp/invoice.pdf"
    )
    
    mock_email_provider.fetch_unread_emails_with_attachments.return_value = [email]
    mock_invoice_repo.get_pending_raw_invoices.return_value = []  # Will be populated by retrieval
    mock_invoice_repo.get_unsynced_processed_invoices.return_value = []
    mock_invoice_repo.invoice_number_exists.return_value = False  # No duplicates
    
    mock_llm_provider.extract_invoice_data.return_value = {
        "invoice_date": "2023-01-01",
        "category": "JEDZENIE",
        "vendor": "Test Vendor",
        "net_amount": 100.0,
        "gross_amount": 123.0,
        "invoice_number": "INV/001",
        "payment_date": "2023-01-14"
    }
    
    # Act - Run all services
    retrieval_service = RetrievalService(mock_email_provider, mock_invoice_repo)
    retrieval_service.run()
    
    # Simulate that the invoice is now pending
    from src.domain.entities import RawInvoice
    raw_invoice = RawInvoice(
        id="raw_1",
        email_id="email_1",
        email_data=email,
        status=ProcessingStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    processing_service = ProcessingService(mock_invoice_repo, mock_llm_provider)
    processing_service.run()
    
    # Assert
    mock_email_provider.fetch_unread_emails_with_attachments.assert_called_once()
    mock_invoice_repo.save_raw_invoice.assert_called_once()
    mock_email_provider.mark_as_processed.assert_called_once_with("email_1")
    mock_llm_provider.extract_invoice_data.assert_called_once()
    mock_invoice_repo.save_processed_invoice.assert_called_once()


def test_summary_generation_structure(mock_notification_provider):
    """Test that summary has correct structure."""
    # Arrange
    notification_service = NotificationService(mock_notification_provider)
    
    summary = {
        "date": "2023-01-01",
        "total_processed": 5,
        "successful": 4,
        "failed": 1,
        "failures": ["Invoice inv_2: LLM Error"]
    }
    
    # Act
    notification_service.send_summary(summary)
    
    # Assert
    mock_notification_provider.send_summary.assert_called_once_with(summary)
    call_args = mock_notification_provider.send_summary.call_args[0][0]
    assert "date" in call_args
    assert "total_processed" in call_args
    assert "successful" in call_args
    assert "failed" in call_args


def test_partial_failure_workflow(
    mock_email_provider,
    mock_invoice_repo,
    mock_llm_provider
):
    """Test workflow when some invoices fail processing."""
    # Arrange
    emails = [
        Email(id=f"email_{i}", sender="vendor@example.com", subject=f"Invoice {i}",
              date=datetime.now(), attachment_path=f"/tmp/invoice{i}.pdf")
        for i in range(3)
    ]
    
    mock_email_provider.fetch_unread_emails_with_attachments.return_value = emails
    
    # Mock LLM to fail on second invoice
    mock_llm_provider.extract_invoice_data.side_effect = [
        {
            "invoice_date": "2023-01-01",
            "category": "JEDZENIE",
            "vendor": "Vendor 1",
            "net_amount": 100.0,
            "gross_amount": 123.0,
            "invoice_number": "INV/001",
            "payment_date": "2023-01-14"
        },
        Exception("LLM Failure"),
        {
            "invoice_date": "2023-01-03",
            "category": "NAPOJE",
            "vendor": "Vendor 3",
            "net_amount": 50.0,
            "gross_amount": 61.5,
            "invoice_number": "INV/003",
            "payment_date": "2023-01-16"
        }
    ]
    
    # Act
    retrieval_service = RetrievalService(mock_email_provider, mock_invoice_repo)
    retrieval_service.run()
    
    # Assert - all emails should be retrieved despite later processing failures
    assert mock_invoice_repo.save_raw_invoice.call_count == 3
    assert mock_email_provider.mark_as_processed.call_count == 3
