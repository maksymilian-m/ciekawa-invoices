# Testing with Sample Data

## Quick Start

1. **Set up your API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Run the test script**:
   ```bash
   uv run python test_sample_workflow.py
   ```

3. **Check the output**:
   - Generated file: `sample_data/output_processed_invoices.csv`
   - Expected file: `sample_data/processed_invoices.csv`

## What It Does

The test script:
1. Reads all PDF files from `sample_data/`
2. Uses the selected LLM (default: Gemini 2.5 Flash Lite) with structured output (Pydantic schema)
3. Extracts invoice data matching the expected CSV format
4. Generates `output_processed_invoices.csv`

## Structured Output

Instead of using a hard-coded prompt with JSON formatting instructions, we now use:
- **Pydantic Model** (`src/domain/invoice_schema.py`): Defines the exact structure
- **Gemini Structured Output**: Guarantees valid JSON matching the schema
- **Type Safety**: All fields are validated automatically

This is much more reliable than the old prompt-based approach!
