"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import yaml

class Settings(BaseSettings):
    """Application settings."""
    
    # GCP Settings
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    gcs_bucket_name: str = "" # GCS Bucket for storing PDFs
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Gmail Settings
    gmail_credentials_path: str = ""
    gmail_token_json: str = "" # Content of token.json for cloud deployment
    
    # Firestore
    firestore_database: str = "(default)"
    
    # Google Sheets
    google_sheets_id: str = ""
    google_sheets_token_json: str = "" # Content of token.json for cloud deployment
    
    # Notification (comma-separated list of emails)
    notification_email: str = "maksymilian.m@gmail.com"
    
    def get_notification_emails(self) -> list[str]:
        """Parse notification emails from comma-separated string."""
        return [email.strip() for email in self.notification_email.split(',') if email.strip()]
    
    # Paths
    categories_file: str = "config/categories.yaml"
    instruction_file: str = "prompts/invoice_extraction_instruction.md"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def load_categories(self) -> list[str]:
        """Load invoice categories from YAML file."""
        categories_path = Path(self.categories_file)
        if not categories_path.exists():
            raise FileNotFoundError(f"Categories file not found: {self.categories_file}")
        
        with open(categories_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('categories', [])
    
    def load_instruction(self) -> str:
        """Load system instruction from markdown file."""
        instruction_path = Path(self.instruction_file)
        if not instruction_path.exists():
            raise FileNotFoundError(f"Instruction file not found: {self.instruction_file}")
        
        with open(instruction_path, 'r', encoding='utf-8') as f:
            return f.read()

# Global settings instance
settings = Settings()
