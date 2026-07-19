"""Application configuration"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "Tammy AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./tammy.db"

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"

    # Email (optional)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""

    # Twilio (optional)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Telnyx (optional)
    telnyx_api_key: str = ""
    telnyx_public_key: str = ""
    telnyx_phone_number: str = ""

    # Telephony
    telephony_provider: str = "telnyx"
    # Public HTTPS base URL this app is reachable at, used to reconstruct the
    # exact webhook URL for signature verification when behind a proxy/load
    # balancer. Falls back to the incoming request's own base URL if unset.
    public_base_url: str = ""

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Timezone
    default_timezone: str = "UTC"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/tammy.log"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
