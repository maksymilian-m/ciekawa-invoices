"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # GCP Settings
    gcp_project_id: str = ""
    gcp_location: str = "us-central1"
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Gmail Settings
    gmail_credentials_path: str = ""
    
    # Firestore
    firestore_database: str = "(default)"
    
    # Google Sheets
    google_sheets_id: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Global settings instance
settings = Settings()
