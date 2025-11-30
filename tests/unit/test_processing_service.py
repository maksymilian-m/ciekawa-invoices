import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from src.services.processing_service import ProcessingService
from src.domain.entities import RawInvoice, ProcessingStatus, Email

@pytest.fixture
def mock_invoice_repo():
    return Mock()

@pytest.fixture
def mock_adk_agent():
    return Mock()

@pytest.fixture
def processing_service(mock_invoice_repo, mock_adk_agent):
    # Note: We'll need to adjust ProcessingService to accept the agent or a factory
    return ProcessingService(mock_invoice_repo, mock_adk_agent)

def test_processing_service_extracts_and_saves(processing_service, mock_invoice_repo, mock_adk_agent):
    # Arrange
    raw_invoice = RawInvoice(
        id="inv_1",
        email_id="email_1",
        email_data=Email(id="e1", sender="s", subject="sub", date=datetime.now(), attachment_path="p"),
        status=ProcessingStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
    
    # Mock ADK response
    mock_adk_agent.run_agent.return_value = {
        "vendor_name": "Test Vendor",
        "total_amount": 100.0,
        "invoice_date": "2023-01-01",
        "items": []
    }

    # Act
    processing_service.run()

    # Assert
    mock_adk_agent.run_agent.assert_called_once_with("p")
    mock_invoice_repo.save_processed_invoice.assert_called_once()
    mock_invoice_repo.update_raw_invoice_status.assert_called_with("inv_1", "PROCESSED")
