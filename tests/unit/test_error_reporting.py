"""Unit tests for error reporting in email notifications."""
import pytest
from unittest.mock import Mock
from datetime import datetime
from src.services.processing_service import ProcessingService
from src.services.notification_service import NotificationService
from src.domain.entities import RawInvoice, ProcessingStatus, Email


@pytest.fixture
def mock_invoice_repo():
    return Mock()


@pytest.fixture
def mock_llm_provider():
    return Mock()


@pytest.fixture
def mock_notification_provider():
    return Mock()


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


class TestProcessingServiceErrorCollection:
    """Tests for error collection in ProcessingService."""
    
    def test_run_returns_errors_list_for_duplicate_invoice(self, mock_invoice_repo, mock_llm_provider):
        """Test that duplicate invoice errors are collected with details."""
        # Arrange
        mock_invoice_repo.invoice_number_exists.return_value = True
        raw_invoice = create_raw_invoice(attachment_path="/tmp/Faktura_001.pdf")
        mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
        
        mock_llm_provider.extract_invoice_data.return_value = {
            "invoice_date": "2023-01-01",
            "category": "JEDZENIE",
            "vendor": "Test Vendor",
            "net_amount": 100.0,
            "gross_amount": 123.0,
            "invoice_number": "INV/001",
            "payment_date": "2023-01-14"
        }
        
        service = ProcessingService(mock_invoice_repo, mock_llm_provider)
        
        # Act
        stats = service.run()
        
        # Assert
        assert 'errors' in stats
        assert len(stats['errors']) == 1
        assert 'Faktura_001.pdf' in stats['errors'][0]['filename']
        assert 'Duplicate' in stats['errors'][0]['reason']
    
    def test_run_returns_empty_errors_list_on_success(self, mock_invoice_repo, mock_llm_provider):
        """Test that successful processing returns empty errors list."""
        # Arrange
        mock_invoice_repo.invoice_number_exists.return_value = False
        raw_invoice = create_raw_invoice()
        mock_invoice_repo.get_pending_raw_invoices.return_value = [raw_invoice]
        
        mock_llm_provider.extract_invoice_data.return_value = {
            "invoice_date": "2023-01-01",
            "category": "JEDZENIE",
            "vendor": "Test Vendor",
            "net_amount": 100.0,
            "gross_amount": 123.0,
            "invoice_number": "INV/001",
            "payment_date": "2023-01-14"
        }
        
        service = ProcessingService(mock_invoice_repo, mock_llm_provider)
        
        # Act
        stats = service.run()
        
        # Assert
        assert 'errors' in stats
        assert len(stats['errors']) == 0


class TestNotificationServiceWithErrors:
    """Tests for NotificationService error handling."""
    
    def test_send_workflow_summary_passes_errors_to_provider(self, mock_notification_provider):
        """Test that errors are passed to the notification provider."""
        # Arrange
        service = NotificationService(mock_notification_provider)
        errors = [
            {'filename': 'invoice1.pdf', 'reason': 'Duplicate invoice: INV/001'},
            {'filename': 'invoice2.pdf', 'reason': 'Invalid date format'}
        ]
        
        # Act
        service.send_workflow_summary(
            retrieved_count=10,
            processed_count=8,
            failed_count=2,
            synced_count=8,
            retried_count=0,
            errors=errors
        )
        
        # Assert
        mock_notification_provider.send_summary.assert_called_once()
        summary = mock_notification_provider.send_summary.call_args[0][0]
        assert 'errors' in summary
        assert len(summary['errors']) == 2
        assert summary['errors'][0]['filename'] == 'invoice1.pdf'


class TestEmailNotificationAdapterErrors:
    """Tests for error rendering in email template."""
    
    def test_email_contains_error_section_when_errors_present(self):
        """Test that email HTML includes error details section."""
        from src.infrastructure.email_notification_adapter import EmailNotificationAdapter
        from unittest.mock import patch
        import base64
        
        # Create adapter with mocked auth
        with patch.object(EmailNotificationAdapter, '_authenticate', return_value=None):
            adapter = EmailNotificationAdapter(recipient_email="test@example.com")
            
            summary = {
                'retrieved': 5,
                'processed': 4,
                'failed': 1,
                'synced': 4,
                'retried': 0,
                'errors': [
                    {'filename': 'Faktura_duplicate.pdf', 'reason': 'Duplicate invoice: INV/001'}
                ]
            }
            
            # Act
            message = adapter._create_message("test@example.com", summary)
            
            # Get the HTML payload (may be base64 encoded)
            payload = message.get_payload()[0].get_payload()
            if isinstance(payload, str) and '\n' in payload and '=' in payload:
                # Likely base64, try to decode
                try:
                    payload = base64.b64decode(payload).decode('utf-8')
                except Exception:
                    pass
            
            # Assert
            assert 'Faktura_duplicate.pdf' in payload
            assert 'Duplicate invoice' in payload
    
    def test_email_no_error_section_when_no_errors(self):
        """Test that email HTML excludes error section when no errors."""
        from src.infrastructure.email_notification_adapter import EmailNotificationAdapter
        from unittest.mock import patch
        import base64
        
        with patch.object(EmailNotificationAdapter, '_authenticate', return_value=None):
            adapter = EmailNotificationAdapter(recipient_email="test@example.com")
            
            summary = {
                'retrieved': 5,
                'processed': 5,
                'failed': 0,
                'synced': 5,
                'retried': 0,
                'errors': []
            }
            
            # Act
            message = adapter._create_message("test@example.com", summary)
            payload = message.get_payload()[0].get_payload()
            if isinstance(payload, str) and '\n' in payload and '=' in payload:
                try:
                    payload = base64.b64decode(payload).decode('utf-8')
                except Exception:
                    pass
            
            # Assert - should not contain error details header
            assert 'Szczegóły błędów' not in payload
