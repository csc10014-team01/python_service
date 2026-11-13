"""Load and validate configuration from the environment and an optional .env file."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    """Application settings; the stub provider works offline without an API key."""

    model_config = ConfigDict(str_strip_whitespace=True, hide_input_in_errors=True)

    data_dir: Path = Path("data")
    llm_provider: str = Field(default="stub", min_length=1)
    llm_api_key: str | None = Field(default=None, repr=False)
    llm_timeout_s: float = Field(default=5.0, gt=0, allow_inf_nan=False)
    llm_model: str = "llama3.2"
    llm_base_url: str | None = None
    kb_dir: Path = Path("data/kb")
    retrieval_kind: Literal["bm25", "tfidf", "hybrid"] = "bm25"
    retrieval_min_score: float = Field(default=2.0, ge=0, allow_inf_nan=False)
    prompt_version: str = "answer_v1"
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, gt=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, gt=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"] = "INFO"

    # Lab04: API and external weather service
    api_admin_key: str | None = Field(default=None, repr=False)
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_timeout_s: float = Field(default=3.0, gt=0, allow_inf_nan=False)
    campus_lat: float = Field(default=10.7626, ge=-90, le=90, allow_inf_nan=False)
    campus_lon: float = Field(default=106.6822, ge=-180, le=180, allow_inf_nan=False)
    rate_limit_per_min: int = Field(default=30, gt=0)
    database_url: str = "sqlite:///assistant.db"
    session_salt: str = Field(default="dev-salt", repr=False)

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_provider_key(self) -> "Settings":
        if self.llm_provider == "openai" and not self.llm_api_key:
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER is 'openai'")
        return self


def load_settings(env_file: str | Path | None = ".env") -> Settings:
    """Read settings, keeping existing environment values ahead of .env values.

    Pass None to read only the process environment. Invalid settings raise
    ConfigError without including environment values or secrets in the message.
    """
    if env_file:
        try:
            load_dotenv(env_file, override=False)
        except (OSError, UnicodeError):
            raise ConfigError("Unable to read the environment file") from None

    try:
        return Settings(
            data_dir=os.getenv("ASSISTANT_DATA_DIR", "data"),
            llm_provider=os.getenv("LLM_PROVIDER", "stub"),
            llm_api_key=os.getenv("LLM_API_KEY") or None,
            llm_timeout_s=os.getenv("LLM_TIMEOUT_S", "5"),
            llm_model=os.getenv("LLM_MODEL", "llama3.2"),
            llm_base_url=os.getenv("LLM_BASE_URL") or None,
            kb_dir=os.getenv("KB_DIR", "data/kb"),
            retrieval_kind=os.getenv("RETRIEVAL_KIND", "bm25"),
            retrieval_min_score=os.getenv("RETRIEVAL_MIN_SCORE", "2.0"),
            prompt_version=os.getenv("PROMPT_VERSION", "answer_v1"),
            credit_rate_vnd=os.getenv("CREDIT_RATE_VND", "450000"),
            retake_multiplier=os.getenv("RETAKE_MULTIPLIER", "1.5"),
            max_credits=os.getenv("MAX_CREDITS", "30"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_admin_key=os.getenv("API_ADMIN_KEY") or None,
            weather_url=os.getenv("WEATHER_URL", "https://api.open-meteo.com/v1/forecast"),
            weather_timeout_s=os.getenv("WEATHER_TIMEOUT_S", "3"),
            campus_lat=os.getenv("CAMPUS_LAT", "10.7626"),
            campus_lon=os.getenv("CAMPUS_LON", "106.6822"),
            rate_limit_per_min=os.getenv("RATE_LIMIT_PER_MIN", "30"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///assistant.db"),
            session_salt=os.getenv("SESSION_SALT", "dev-salt"),
        )
    except ValidationError as exc:
        fields = sorted({".".join(map(str, error["loc"])) or "settings" for error in exc.errors()})
        if any("LLM_API_KEY is required" in error["msg"] for error in exc.errors()):
            raise ConfigError("LLM_API_KEY is required when LLM_PROVIDER is 'openai'") from None
        raise ConfigError(f"Invalid configuration: {', '.join(fields)}") from None
