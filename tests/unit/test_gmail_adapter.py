"""Unit tests for GmailAdapter."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from googleapiclient.errors import HttpError
from src.infrastructure.gmail_adapter import GmailAdapter
from src.domain.entities import Email


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    return Mock()


@pytest.fixture
def gmail_adapter_with_mock_service(mock_gmail_service):
    """Gmail adapter with mocked service."""
    with patch('src.infrastructure.gmail_adapter.build', return_value=mock_gmail_service):
        with patch('src.infrastructure.gmail_adapter.Credentials'):
            with patch('os.path.exists', return_value=True):
                adapter = GmailAdapter(credentials_path="fake_creds.json")
                adapter.service = mock_gmail_service
                return adapter


def test_no_unread_emails(gmail_adapter_with_mock_service, mock_gmail_service):
    """Test when there are no unread emails."""
    # Arrange
    mock_gmail_service.users().messages().list().execute.return_value = {}
    
    # Act
    emails = gmail_adapter_with_mock_service.fetch_unread_emails_with_attachments()
    
    # Assert
    assert emails == []
    # Verify the list method was called with correct parameters
    mock_gmail_service.users().messages().list.assert_called_with(userId='me', q='is:unread has:attachment')


def test_email_without_pdf_attachment(gmail_adapter_with_mock_service, mock_gmail_service):
    """Test email with non-PDF attachments only."""
    # Arrange
    mock_gmail_service.users().messages().list().execute.return_value = {
        'messages': [{'id': 'msg1'}]
    }
    
    mock_gmail_service.users().messages().get().execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test'},
                {'name': 'From', 'value': 'test@example.com'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00'}
            ],
            'parts': [
                {
                    'filename': 'image.jpg',
                    'body': {'attachmentId': 'att1'}
                }
            ]
        },
        'snippet': 'Test email'
    }
    
    # Act
    emails = gmail_adapter_with_mock_service.fetch_unread_emails_with_attachments()
    
    # Assert
    assert emails == []


def test_email_with_multiple_attachments_including_pdf(gmail_adapter_with_mock_service, mock_gmail_service):
    """Test email with multiple attachments where one is a PDF."""
    # Arrange
    mock_gmail_service.users().messages().list().execute.return_value = {
        'messages': [{'id': 'msg1'}]
    }
    
    mock_gmail_service.users().messages().get().execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Invoice'},
                {'name': 'From', 'value': 'vendor@example.com'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00'}
            ],
            'parts': [
                {
                    'filename': 'image.jpg',
                    'body': {'attachmentId': 'att1'}
                },
                {
                    'filename': 'invoice.pdf',
                    'body': {'attachmentId': 'att2'}
                }
            ]
        },
        'snippet': 'Invoice attached'
    }
    
    mock_gmail_service.users().messages().attachments().get().execute.return_value = {
        'data': 'ZmFrZSBwZGYgZGF0YQ=='  # base64 encoded "fake pdf data"
    }
    
    # Act
    emails = gmail_adapter_with_mock_service.fetch_unread_emails_with_attachments()
    
    # Assert
    assert len(emails) == 1
    assert emails[0].id == 'msg1'
    assert emails[0].subject == 'Invoice'
    assert 'invoice.pdf' in emails[0].attachment_path


def test_gmail_api_error(gmail_adapter_with_mock_service, mock_gmail_service):
    """Test handling of Gmail API errors."""
    # Arrange
    mock_gmail_service.users().messages().list().execute.side_effect = HttpError(
        resp=Mock(status=500),
        content=b'Internal Server Error'
    )
    
    # Act
    emails = gmail_adapter_with_mock_service.fetch_unread_emails_with_attachments()
    
    # Assert
    assert emails == []


def test_mark_as_processed_success(gmail_adapter_with_mock_service, mock_gmail_service):
    """Test successfully marking email as processed."""
    # Arrange
    email_id = "msg123"
    
    # Act
    gmail_adapter_with_mock_service.mark_as_processed(email_id)
    
    # Assert
    mock_gmail_service.users().messages().modify.assert_called_once()
    call_args = mock_gmail_service.users().messages().modify.call_args
    assert call_args[1]['id'] == email_id
    assert 'UNREAD' in call_args[1]['body']['removeLabelIds']
