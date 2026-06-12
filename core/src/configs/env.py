from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    port: int = Field(default=8000, ge=1, le=65535)
    host: str = Field(default="0.0.0.0")
    mt_model: str = Field(min_length=1)
    source_language_default: str = Field(min_length=1)
    target_language_default: str = Field(min_length=1)
    model_cache_dir: str = Field(default="/model_cache")
    max_input_chars: int = Field(default=1000, gt=0)
    log_level: str = Field(default="INFO")

    @property
    def model_label(self) -> str:
        return self.mt_model.rstrip("/").split("/")[-1] or self.mt_model

    def public_dict(self) -> dict[str, str | int]:
        return {
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "mt_model": self.mt_model,
            "model_cache_dir": self.model_cache_dir,
            "source_language_default": self.source_language_default,
            "target_language_default": self.target_language_default,
            "max_input_chars": self.max_input_chars,
        }


settings = Settings()
