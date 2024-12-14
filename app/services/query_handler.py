import requests
from app.utils.logger import get_logger
from config.settings import openrouter_settings

logger = get_logger()

async def process_query(query: str) -> str:
    try:
        payload = {"query": query}
        headers = {"Authorization": f"Bearer {openrouter_settings.API_KEY}"}
        response = requests.post(openrouter_settings.API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("response", "Sorry, I couldn't process that.")
    except Exception as e:
        logger.error(f"Error in process_query: {e}")
        return "There was an error processing your query."