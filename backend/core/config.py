# backend/core/config.py
from pathlib import Path
import dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Always find .env relative to this file, not the working directory
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
dotenv.load_dotenv(str(_ENV_FILE), override=True)

class Settings(BaseSettings):
    GROQ_API_KEY: str = Field(default="")
    GROQ_ORCHESTRATOR_MODEL: str = "llama3-70b-8192"
    GROQ_TOOL_MODEL: str = "llama3-8b-8192"
    GROQ_EMBEDDING_MODEL: str = "nomic-embed-text-v1.5"
    DATABASE_URL: str = "sqlite+aiosqlite:///./innervoice.db"
    SECRET_KEY: str = "9a263158c5c7db8bf1db884b23267d3e69f4ea5fb54d68ab73a388b3be89520c"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    APP_ENV: str = "development"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    MAX_REASONING_ITERATIONS: int = 8
    MAX_FOLLOWUP_TURNS: int = 2
    AGENT_TIMEOUT_SECONDS: int = 90

    model_config = {
        "extra": "ignore"
    }

settings = Settings()
