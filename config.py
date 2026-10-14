import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ecobot-green-campus-secret-key-2026")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "green_campus.db")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
