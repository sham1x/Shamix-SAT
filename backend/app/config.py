import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./backend/data/shamix.db"
    ALLOWED_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"
    PORT: int = 8080

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be set in environment/.env and be at least 32 characters long")
        v_lower = v.lower()
        if v.startswith("CHANGE_ME") or "default" in v_lower:
            raise ValueError("Insecure or placeholder SECRET_KEY rejected. Generate a secure random key.")
        return v

settings = Settings()
