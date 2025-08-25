from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "Smart Content Moderator API"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/content_moderator"
    
    # Google Gemini API
    gemini_api_key: str
    
    # Slack Configuration
    slack_webhook_url: Optional[str] = None
    
    # Brevo Email API
    brevo_api_key: Optional[str] = None
    brevo_sender_email: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

