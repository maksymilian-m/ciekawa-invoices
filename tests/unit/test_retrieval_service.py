import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from src.services.retrieval_service import RetrievalService
from src.domain.entities import Email, RawInvoice, ProcessingStatus

@pytest.fixture
def mock_email_provider():
    return Mock()

@pytest.fixture
def mock_invoice_repo():
    return Mock()

@pytest.fixture
def retrieval_service(mock_email_provider, mock_invoice_repo):
    return RetrievalService(mock_email_provider, mock_invoice_repo)

def test_retrieval_service_fetches_and_saves_emails(retrieval_service, mock_email_provider, mock_invoice_repo):
    # Arrange
    email = Email(
        id="email_1",
        sender="vendor@example.com",
        subject="Invoice 123",
        date=datetime.now(),
        attachment_path="/tmp/invoice.pdf"
    )
    mock_email_provider.fetch_unread_emails_with_attachments.return_value = [email]

    # Act
    retrieval_service.run()

    # Assert
    mock_email_provider.fetch_unread_emails_with_attachments.assert_called_once()
    mock_invoice_repo.save_raw_invoice.assert_called_once()
    saved_invoice = mock_invoice_repo.save_raw_invoice.call_args[0][0]
    assert isinstance(saved_invoice, RawInvoice)
    assert saved_invoice.email_id == "email_1"
    assert saved_invoice.status == ProcessingStatus.PENDING
    
    mock_email_provider.mark_as_processed.assert_called_once_with("email_1")

def test_retrieval_service_handles_exception(retrieval_service, mock_email_provider, mock_invoice_repo):
    # Arrange
    email = Email(
        id="email_1",
        sender="vendor@example.com",
        subject="Invoice 123",
        date=datetime.now(),
        attachment_path="/tmp/invoice.pdf"
    )
    mock_email_provider.fetch_unread_emails_with_attachments.return_value = [email]
    mock_invoice_repo.save_raw_invoice.side_effect = Exception("DB Error")

    # Act
    retrieval_service.run()

    # Assert
    # Should log error and NOT mark as processed (or handle accordingly)
    mock_invoice_repo.save_raw_invoice.assert_called_once()
    mock_email_provider.mark_as_processed.assert_not_called()
