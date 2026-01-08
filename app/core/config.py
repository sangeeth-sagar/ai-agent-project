import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DB_DSN: str = os.getenv("DB_DSN", "postgresql://postgres:Sangeeth%40123@localhost:5432/ai_agent_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_key_123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10  # <--- SET TO 10 MINUTES

settings = Settings()