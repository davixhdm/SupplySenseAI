import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    APP_NAME: str = "SupplySense AI"
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_ENGINE_API_KEY: str = os.getenv("AI_ENGINE_API_KEY", "supplysense449840e02cf67e93")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Hdm@2002")
    ADMIN_PASSWORD2: str = os.getenv("ADMIN_PASSWORD2", "SupplySense@2026")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"

settings = Settings()