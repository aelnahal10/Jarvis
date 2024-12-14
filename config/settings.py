import os
from dotenv import load_dotenv

load_dotenv()

class OpenRouterSettings:
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    API_URL = os.getenv("OPENROUTER_API_URL")

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

settings = Settings()
openrouter_settings = OpenRouterSettings()