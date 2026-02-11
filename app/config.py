import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-change-me")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = ".flask_sessions"
    SESSION_PERMANENT = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")