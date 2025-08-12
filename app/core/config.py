from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # SECRETS - aka sensitive data
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")

    # CONFIGURATION - non-sensitive
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expires_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Application config
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Database config (non-sensitive parts)
    database_name: str = Field("filebase", env="DATABASE_NAME")
    database_host: str = Field("localhost", env="DATABASE_HOST")
    database_port: int = Field(5432, env="DATABASE_PORT")

    # Redis config
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")

    @property
    def redis_url(self) -> str:
        """Construct the Redis URL for Celery broker and backend."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @validator("jwt_secret_key")
    def validate_jwt_secrets(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production.")
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


from functools import lru_cache


@lru_cache()
def get_settings() -> Settings:
    return Settings()
