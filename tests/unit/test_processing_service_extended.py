"""Extended unit tests for ProcessingService."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
from src.services.processing_service import ProcessingService
from src.domain.entities import RawInvoice, ProcessingStatus, Email


@pytest.fixture
def mock_invoice_repo():
    return Mock()


@pytest.fixture
def mock_llm_provider():
    return Mock()


@pytest.fixture
def processing_service(mock_invoice_repo, mock_llm_provider):
    # Set default return value for invoice_number_exists
    mock_invoice_repo.invoice_number_exists.return_value = False
    return ProcessingService(mock_invoice_repo, mock_llm_provider)


def create_raw_invoice(invoice_id="inv_1", email_id="email_1", attachment_path="/tmp/test.pdf"):
    """Helper to create a raw invoice for testing."""
    return RawInvoice(
        id=invoice_id,
        email_id=email_id,
        email_data=Email(
            id=email_id,
            sender="vendor@example.com",
            subject="Invoice",
            date=datetime.now(),
            attachment_path=attachment_path
        ),
        status=ProcessingStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def test_llm_429_error_with_retry(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test that 429 errors trigger retry logic."""
    # Arrange
    raw_invoice = create_raw_invoice()
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    # Mock LLM to fail twice with 429, then succeed
    mock_llm_provider.extract_invoice_data.side_effect = [
        ResourceExhausted("Rate limit exceeded"),
        ResourceExhausted("Rate limit exceeded"),
        {
            "invoice_date": "2023-01-01",
            "category": "JEDZENIE",
            "vendor": "Test Vendor",
            "net_amount": 100.0,
            "gross_amount": 123.0,
            "invoice_number": "INV/001",
            "payment_date": "2023-01-14"
        }
    ]
    
    # Act
    processing_service.run()
    
    # Assert
    assert mock_llm_provider.extract_invoice_data.call_count == 3
    mock_invoice_repo.save_processed_invoice.assert_called_once()
    mock_invoice_repo.update_raw_invoice_status.assert_called_with("inv_1", "PROCESSED")


def test_llm_returns_invalid_data(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test handling of invalid LLM response data."""
    # Arrange
    raw_invoice = create_raw_invoice()
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    # Mock LLM to return invalid data (missing required fields)
    mock_llm_provider.extract_invoice_data.return_value = {
        "invoice_date": "invalid-date",
        "category": "JEDZENIE"
        # Missing other required fields
    }
    
    # Act
    processing_service.run()
    
    # Assert
    mock_invoice_repo.save_processed_invoice.assert_not_called()
    # Verify it was marked as failed with an error message
    # Note: status update is called twice (once in _process_single_invoice, once in run)
    calls = mock_invoice_repo.update_raw_invoice_status.call_args_list
    assert len(calls) >= 1
    # Check that at least one call was for FAILED status
    failed_calls = [c for c in calls if c[0][1] == "FAILED"]
    assert len(failed_calls) >= 1
    assert failed_calls[0][0][0] == "inv_1"
    assert failed_calls[0][0][2] is not None  # Error message should exist


def test_batch_processing_with_partial_failures(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test that batch processing continues even when some invoices fail."""
    # Arrange
    invoice1 = create_raw_invoice("inv_1", "email_1", "/tmp/test1.pdf")
    invoice2 = create_raw_invoice("inv_2", "email_2", "/tmp/test2.pdf")
    invoice3 = create_raw_invoice("inv_3", "email_3", "/tmp/test3.pdf")
    
    mock_invoice_repo.get_pending_raw_invoices.return_value = [invoice1, invoice2, invoice3]
    
    # Mock LLM: first succeeds, second fails, third succeeds
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
        Exception("LLM Error"),
        {
            "invoice_date": "2023-01-02",
            "category": "NAPOJE",
            "vendor": "Vendor 3",
            "net_amount": 50.0,
            "gross_amount": 61.5,
            "invoice_number": "INV/003",
            "payment_date": "2023-01-15"
        }
    ]
    
    # Act
    processing_service.run()
    
    # Assert
    assert mock_invoice_repo.save_processed_invoice.call_count == 2
    # Note: update_raw_invoice_status is called twice for failed invoice (once in _process_single_invoice, once in run)
    # So we expect 4 total calls: 2 success + 2 for the failed one
    assert mock_invoice_repo.update_raw_invoice_status.call_count >= 3
    
    # Verify invoice 2 was marked as failed
    failed_calls = [call for call in mock_invoice_repo.update_raw_invoice_status.call_args_list 
                    if call[0][1] == "FAILED"]
    assert len(failed_calls) >= 1
    assert any(call[0][0] == "inv_2" for call in failed_calls)


def test_duplicate_invoice_detection(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test that duplicate invoices (same invoice_number) are detected."""
    # Arrange
    raw_invoice = create_raw_invoice()
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    # Mock that an invoice with this number already exists
    mock_invoice_repo.invoice_number_exists.return_value = True
    
    mock_llm_provider.extract_invoice_data.return_value = {
        "invoice_date": "2023-01-01",
        "category": "JEDZENIE",
        "vendor": "Test Vendor",
        "net_amount": 100.0,
        "gross_amount": 123.0,
        "invoice_number": "INV/001",
        "payment_date": "2023-01-14"
    }
    
    # Act
    processing_service.run()
    
    # Assert - should not save if duplicate
    mock_invoice_repo.invoice_number_exists.assert_called_once_with("INV/001")
    mock_invoice_repo.save_processed_invoice.assert_not_called()
    # Should be marked as failed with duplicate message
    failed_calls = [c for c in mock_invoice_repo.update_raw_invoice_status.call_args_list 
                    if c[0][1] == "FAILED"]
    assert len(failed_calls) >= 1
    assert "Duplicate" in failed_calls[0][0][2]


def test_processing_service_extracts_and_saves(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test successful invoice processing and saving."""
    # Arrange
    raw_invoice = create_raw_invoice()
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    mock_llm_provider.extract_invoice_data.return_value = {
        "invoice_date": "2023-01-01",
        "category": "JEDZENIE",
        "vendor": "Test Vendor",
        "net_amount": 80.0,
        "gross_amount": 100.0,
        "invoice_number": "INV/001",
        "payment_date": "2023-01-14"
    }
    
    # Act
    processing_service.run()
    
    # Assert
    mock_llm_provider.extract_invoice_data.assert_called_once()
    mock_invoice_repo.save_processed_invoice.assert_called_once()
    mock_invoice_repo.update_raw_invoice_status.assert_called_with("inv_1", "PROCESSED")


def test_multiple_date_formats_handled(processing_service, mock_invoice_repo, mock_llm_provider):
    """Test that various date formats are handled correctly."""
    # Arrange
    raw_invoice = create_raw_invoice()
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    # Test with Polish date format
    mock_llm_provider.extract_invoice_data.return_value = {
        "invoice_date": "01.01.2023",  # DD.MM.YYYY format
        "category": "JEDZENIE",
        "vendor": "Test Vendor",
        "net_amount": 80.0,
        "gross_amount": 100.0,
        "invoice_number": "INV/001",
        "payment_date": "14.01.2023"
    }
    
    # Act
    processing_service.run()
    
    # Assert
    mock_invoice_repo.save_processed_invoice.assert_called_once()
    saved_invoice = mock_invoice_repo.save_processed_invoice.call_args[0][0]
    assert saved_invoice.extracted_data.invoice_date.year == 2023
    assert saved_invoice.extracted_data.invoice_date.month == 1
    assert saved_invoice.extracted_data.invoice_date.day == 1
