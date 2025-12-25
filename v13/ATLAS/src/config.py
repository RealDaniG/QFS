import os
from pydantic_settings import BaseSettings

from v13.libs.PQC import PQC, KeyPair, ValidationResult
from v13.atlas.src.qfs_client import QFSClient
from v13.atlas.src.qfs_types import OperationBundle


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8001"))  # Default to 8001 (ATLAS v18 standard)

    # CORS
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000"
    )

    # Auth
    SESSION_SECRET: str = os.getenv(
        "SESSION_SECRET", "dev-secret-change-in-prod-atlas-v18"
    )
    SESSION_EXPIRY_HOURS: int = 24

    # Database (future)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./atlas_v18.db")

    # Feature flags
    ENABLE_DAILY_REWARDS: bool = True
    EXPLAIN_THIS_SOURCE: str = "qfs_ledger"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra env vars


settings = Settings()
EXPLAIN_THIS_SOURCE = settings.EXPLAIN_THIS_SOURCE
