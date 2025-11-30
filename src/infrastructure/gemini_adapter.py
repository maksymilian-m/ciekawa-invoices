"""Gemini LLM Adapter using google-genai SDK with structured output."""
import logging
import base64
from pathlib import Path
from google import genai
from google.genai import types
from src.ports.interfaces import LLMProvider
from src.domain.invoice_schema import InvoiceExtraction
from src.config import settings

logger = logging.getLogger(__name__)

class GeminiAdapter(LLMProvider):
    """Gemini LLM adapter for invoice extraction with structured output."""
    
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        
        if not self.api_key:
            logger.warning("No Gemini API key provided - running in mock mode")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized GeminiAdapter with model: {self.model_name}")

    def extract_invoice_data(self, file_path: str) -> dict:
        """Extract invoice data from PDF using Gemini with structured output."""
        if not self.client:
            logger.warning("Running in mock mode - returning dummy data")
            return {
                "invoice_date": "2023-10-27",
                "category": "JEDZENIE",
                "vendor": "Mock Vendor",
                "net_amount": 123.45,
                "gross_amount": 151.84,
                "invoice_number": "MOCK/001/2023",
                "payment_date": "2023-11-10"
            }
        
        try:
            # Read PDF file
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            with open(pdf_path, "rb") as f:
                pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Load system instruction from file
            system_instruction = settings.load_instruction()
            
            # Generate content with structured output
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(
                        data=base64.standard_b64decode(pdf_data),
                        mime_type="application/pdf"
                    ),
                    "Extract the invoice information from this PDF."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=InvoiceExtraction
                )
            )
            
            # Parse response
            result = response.text
            logger.info(f"Successfully extracted invoice data from {file_path}")
            logger.debug(f"Raw response: {result}")
            
            # The response should already be a JSON string matching our schema
            import json
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Failed to extract invoice data from {file_path}: {e}")
            raise
