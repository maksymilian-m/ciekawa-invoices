"""Test script to process sample invoices and generate CSV output."""
import logging
import csv
from pathlib import Path
from datetime import datetime
from src.infrastructure.gemini_adapter import GeminiAdapter
from src.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_sample_invoices():
    """Process all sample PDFs and generate CSV output."""
    
    # Initialize the LLM adapter
    llm = GeminiAdapter()
    
    # Sample data directory
    sample_dir = Path("sample_data")
    output_file = sample_dir / "output_processed_invoices.csv"
    
    # Find all PDF files
    pdf_files = list(sample_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    results = []
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing {pdf_file.name}...")
            extracted_data = llm.extract_invoice_data(str(pdf_file))
            
            # Convert to CSV row format
            row = {
                "Data wstawienia": extracted_data["invoice_date"],
                "PŁATNOŚĆ ZA": extracted_data["category"],
                "FIRMA / KONTRAHENT": extracted_data["vendor"],
                "NETTO": f"{extracted_data['net_amount']:.2f}".replace('.', ','),
                "KWOTA BRUTTO": f"{extracted_data['gross_amount']:.2f}".replace('.', ','),
                "NR FV": extracted_data["invoice_number"],
                "TERMIN PŁATNOŚCI": extracted_data["payment_date"]
            }
            results.append(row)
            logger.info(f"✓ Successfully processed {pdf_file.name}")
            
        except Exception as e:
            logger.error(f"✗ Failed to process {pdf_file.name}: {e}")
    
    # Write to CSV
    if results:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["Data wstawienia", "PŁATNOŚĆ ZA", "FIRMA / KONTRAHENT", 
                         "NETTO", "KWOTA BRUTTO", "NR FV", "TERMIN PŁATNOŚCI"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"\n✓ Successfully wrote {len(results)} invoices to {output_file}")
        logger.info(f"\nCompare with expected output: {sample_dir / 'processed_invoices.csv.txt'}")
    else:
        logger.warning("No invoices were successfully processed")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Ciekawa Invoices - Sample Data Test")
    logger.info("=" * 60)
    
    # Check if API key is set
    if not settings.gemini_api_key:
        logger.error("\n❌ GEMINI_API_KEY not set!")
        logger.info("Please create a .env file with your API key:")
        logger.info("  GEMINI_API_KEY=your-api-key-here")
        exit(1)
    
    process_sample_invoices()
