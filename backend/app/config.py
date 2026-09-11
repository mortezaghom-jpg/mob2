"""
تنظیمات مرکزی برنامه.
تمام مقادیر حساس (کلید AI و ...) از فایل .env خوانده می‌شوند و هرگز Hard-Code نیستند.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_BASE_URL: str = "https://api.openai.com/v1"

    DATABASE_URL: str = "sqlite:///./tanakhah.db"

    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    ALLOWED_ORIGINS: str = "*"


settings = Settings()
