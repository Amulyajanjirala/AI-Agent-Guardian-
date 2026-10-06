import os
from pathlib import Path
from typing import List

# Determine Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Lightweight .env loader if python-dotenv is not installed
def load_env_file(path: Path) -> None:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = value

load_env_file(ENV_PATH)

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Agent Guardian")
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-guardian-secret-key-replace-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Database
    DATABASE_PATH: Path = BASE_DIR / "data" / "guardian.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM Settings (for Version 2+)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "").lower()
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "")
    KIMI_MODEL: str = os.getenv("KIMI_MODEL", "moonshot-v1-32k")
    KIMI_BASE_URL: str = os.getenv("KIMI_BASE_URL") or os.getenv("KIMI_API_BASE_URL", "https://api.moonshot.cn/v1")
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

settings = Settings()
