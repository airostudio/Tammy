"""Application configuration"""

import os
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

    # Admin section - single shared password gating /admin and the
    # underlying data API. Empty means the admin section is disabled.
    # This is the legacy path used by the built-in public/admin/ dashboard;
    # the Next.js frontend (web/) instead authenticates via Supabase Auth
    # below.
    admin_password: str = ""

    # Supabase Auth - lets the Next.js frontend's Supabase session tokens
    # authenticate against this API (see app/api/deps.py). From the
    # Supabase Dashboard: Project Settings -> API -> JWT Settings -> JWT
    # Secret. Leave blank to disable Supabase-token auth (admin_password
    # above still works either way).
    supabase_jwt_secret: str = ""

    # The deployed Next.js frontend's URL (no trailing slash), e.g.
    # https://tammy.vercel.app. Used to send the browser back to the right
    # place after a calendar OAuth connection completes. Leave blank to
    # fall back to the legacy public/admin/ dashboard on this same origin.
    frontend_url: str = ""

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
    # balancer, and as the OAuth redirect_uri base for calendar sync. Falls
    # back to the incoming request's own base URL if unset.
    public_base_url: str = ""

    # Google Calendar OAuth (optional) - from a Google Cloud OAuth 2.0
    # Client (console.cloud.google.com/apis/credentials) with the Calendar
    # API enabled.
    google_client_id: str = ""
    google_client_secret: str = ""

    # Microsoft 365/Outlook OAuth (optional) - from an Azure AD app
    # registration (portal.azure.com) with Microsoft Graph's
    # Calendars.ReadWrite delegated permission.
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""

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
    settings = Settings()

    if os.getenv("VERCEL") and settings.database_url.startswith("sqlite"):
        # Vercel's serverless filesystem is read-only outside /tmp - a
        # relative-path sqlite file (the local-dev default) would crash the
        # function on write. Redirect to /tmp so the app can boot; this is
        # still ephemeral per-invocation, so anything that needs to persist
        # across requests needs a real DATABASE_URL (e.g. Postgres) set in
        # the Vercel project's environment variables.
        path = settings.database_url.split(":///", 1)[-1] if ":///" in settings.database_url else ""
        if not path.startswith("/"):
            settings.database_url = "sqlite+aiosqlite:////tmp/tammy.db"

    # Hosted Postgres providers (Supabase, Neon, Railway, Heroku...) hand
    # out plain "postgresql://" or legacy "postgres://" URLs. SQLAlchemy's
    # async engine needs an explicit async driver in the scheme, or engine
    # creation fails outright (defaults to the sync psycopg2 driver, which
    # isn't installed and isn't async-compatible anyway).
    if settings.database_url.startswith("postgres://"):
        settings.database_url = settings.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif settings.database_url.startswith("postgresql://"):
        settings.database_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    return settings
