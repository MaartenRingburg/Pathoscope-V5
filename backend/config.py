import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    # Flask secret key for sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')

    # Gemini (Google’s generative AI) API key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Path to your Firebase service account JSON
    FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH')

    # Celery settings (uses Redis by default)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
