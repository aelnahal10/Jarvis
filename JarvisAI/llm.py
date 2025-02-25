import requests
from Jarvis.config import config

HUGGINGFACE_API_KEY = config.huggingface_api_key
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

def ask_llm(prompt):
    """Uses Hugging Face API to get an AI-generated response."""
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{LLM_MODEL}",
        headers=headers, json=payload
    )

    if response.status_code == 200:
        return response.json()[0].get("generated_text", "I couldn't process that request.")
    
    return "Failed to get response from AI."
