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
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, gt=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, gt=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"] = "INFO"

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_provider_key(self) -> "Settings":
        if self.llm_provider != "stub" and not self.llm_api_key:
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER is not 'stub'")
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
            credit_rate_vnd=os.getenv("CREDIT_RATE_VND", "450000"),
            retake_multiplier=os.getenv("RETAKE_MULTIPLIER", "1.5"),
            max_credits=os.getenv("MAX_CREDITS", "30"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    except ValidationError as exc:
        fields = sorted({".".join(map(str, error["loc"])) or "settings" for error in exc.errors()})
        if any("LLM_API_KEY is required" in error["msg"] for error in exc.errors()):
            raise ConfigError("LLM_API_KEY is required when LLM_PROVIDER is not 'stub'") from None
        raise ConfigError(f"Invalid configuration: {', '.join(fields)}") from None
