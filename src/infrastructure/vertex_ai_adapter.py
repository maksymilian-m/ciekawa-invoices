import logging
from src.ports.interfaces import AgentProvider

logger = logging.getLogger(__name__)

class VertexAIAdapter(AgentProvider):
    def __init__(self, project_id: str | None = None, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        # TODO: Initialize Vertex AI / ADK Agent
        logger.info("Initialized VertexAIAdapter (Mock Mode)")

    def run_agent(self, file_path: str) -> dict:
        # TODO: 
        # 1. Upload file to GCS or read content
        # 2. Invoke ADK Agent with file
        # 3. Parse response
        logger.info(f"Running Agent on file {file_path} (Mock)...")
        return {
            "vendor_name": "Mock Vendor",
            "total_amount": 123.45,
            "invoice_date": "2023-10-27",
            "items": []
        }
