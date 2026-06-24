from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent

REPO_DIR = BASE_DIR / "data" / "repos"

REPO_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")