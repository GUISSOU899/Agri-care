from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri-Care"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/agricare"

    # ✅ Ajout OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SEED: int = int(os.getenv("SEED", "42"))
    ML_URL: Optional[str] = os.getenv("ML_URL", None)

    # AUTH / SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_ENV_FILE_IMPORTANT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@agri-care.local")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin123!ChangeMe")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()

