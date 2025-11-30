"""Real Vertex AI Adapter using Google ADK and Gemini."""
import logging
import base64
from pathlib import Path
from google import genai
from google.genai import types
from src.ports.interfaces import AgentProvider
from src.domain.invoice_schema import InvoiceExtraction
from src.config import settings

logger = logging.getLogger(__name__)

class VertexAIAdapter(AgentProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        
        if not self.api_key:
            logger.warning("No Gemini API key provided - running in mock mode")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized VertexAIAdapter with model: {self.model_name}")

    def run_agent(self, file_path: str) -> dict:
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
            
            # Create system instruction
            system_instruction = """You are a helpful office assistant for a local Warsaw bistro. 
Your role is to extract key information from invoice PDFs in Polish.

Extract the following information:
- Invoice Date (Data wystawienia)
- Category: Classify into one of: JEDZENIE, NAPOJE, ALKOHOL, ADMINISTRACYJNE, BANK, BAR, CHEMIA, CIASTA, DOSTAWY, GAZ, IMPREZY, INNE RACHUNKI, KAWA, KONCESJA, LODY, LÓD, PODATEK, PRĄD, REKLAMA, REMONT, ŚMIECIE, UBEZPIECZENIE, WODA, WYPOSAŻENIE
- Vendor name (Sprzedawca)
- Net amount (Kwota netto)
- Gross amount (Kwota brutto)
- Invoice number (Numer faktury)
- Payment date (Termin płatności)

Use Polish date format and comma as decimal separator in your understanding, but output dates in YYYY-MM-DD format and numbers as floats."""

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
