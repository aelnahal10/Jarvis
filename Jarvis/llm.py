import requests
import Jarvis.config as config

HUGGINGFACE_API_KEY = config.huggingface_api_key
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

def ask_llm(prompt):
    """Uses Hugging Face API to get an AI-generated response with better error handling."""
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{LLM_MODEL}",
            headers=headers, json=payload, timeout=10  # Set request timeout
        )

        if response.status_code == 200:
            json_response = response.json()
            if isinstance(json_response, list) and len(json_response) > 0:
                return json_response[0].get("generated_text", "I couldn't process that request.")
            return "AI response was empty."

        elif response.status_code == 503:
            return "The AI model is currently busy. Try again later."

        else:
            return f"Error: Received unexpected status code {response.status_code}"

    except requests.exceptions.Timeout:
        return "Request to AI timed out. Try again."

    except requests.exceptions.RequestException as e:
        return f"Failed to connect to AI service: {str(e)}"
