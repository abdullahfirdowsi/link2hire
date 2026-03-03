"""
Configuration management for Link2Hire application.
All environment variables and application settings are centralized here.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Settings
    app_name: str = "Link2Hire"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Azure OpenAI Settings
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_temperature: float = 0.0
    azure_openai_max_tokens: int = 2000
    
    # MongoDB Settings
    mongodb_connection_string: str
    mongodb_database_name: str = "link2hire"
    mongodb_collection_jobs: str = "jobs"
    mongodb_collection_conversations: str = "conversations"
    
    # Google Sheets Settings
    google_sheets_credentials_path: str
    google_sheets_spreadsheet_id: str
    google_sheets_worksheet_name: str = "Jobs"
    
    # LinkedIn Settings (Future)
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_redirect_uri: Optional[str] = None
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list = ["http://localhost:4200", "http://localhost:3000"]
    
    # Timeouts and Limits
    request_timeout: int = 30
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use lru_cache to ensure single instance across application.
    """
    return Settings()


# Export settings instance
settings = get_settings()
