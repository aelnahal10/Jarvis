from fastapi import FastAPI, Request, BackgroundTasks
from gtts import gTTS
import redis
import requests
import os
import json

app = FastAPI()

# Initialize Redis for session management
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# LLM API Details (e.g., Hugging Face)
LLM_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
LLM_API_KEY = "your_huggingface_api_key"  # Replace with your Hugging Face API key

# TTS Directory
TTS_AUDIO_DIR = "audio/"
os.makedirs(TTS_AUDIO_DIR, exist_ok=True)

# Helper: Send query to LLM API
def send_to_llm(query: str) -> str:
    """
    Sends the user's query to a Large Language Model API.
    """
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    payload = {"inputs": query}
    try:
        response = requests.post(LLM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("generated_text", "Sorry, I couldn't generate a response.")
    except Exception as e:
        print(f"Error with LLM API: {e}")
        return "There was an error processing your request."

# Helper: Generate TTS audio file
def generate_tts(text: str, session_id: str) -> str:
    """
    Converts text to speech and saves it as an audio file.
    """
    audio_file = f"{TTS_AUDIO_DIR}{session_id}.mp3"
    tts = gTTS(text)
    tts.save(audio_file)
    # Assuming you use ngrok to serve the files
    ngrok_url = "https://50ed-92-40-183-65.ngrok-free.app"  # Replace with your actual ngrok public URL
    return f"{ngrok_url}/{audio_file}"

@app.post("/alexa/intent")
async def handle_alexa_request(request: Request, background_tasks: BackgroundTasks):
    """
    Handles Alexa skill requests.
    """
    # Parse the incoming Alexa request
    data = await request.json()
    session_id = data.get("session", {}).get("sessionId")
    user_query = data.get("request", {}).get("intent", {}).get("slots", {}).get("query", {}).get("value", "")
    
    if not session_id or not user_query:
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I didn't understand that. Can you try again?"
                },
                "shouldEndSession": False
            }
        }

    # Retrieve or initialize session data from Redis
    session_data = redis_client.get(session_id)
    if not session_data:
        session_data = {"history": []}
    else:
        session_data = json.loads(session_data)

    # Add the user's query to session history
    session_data["history"].append(user_query)

    # Save updated session data to Redis
    redis_client.set(session_id, json.dumps(session_data))

    # Generate LLM response in a background task
    response_text = send_to_llm(user_query)

    # Generate TTS audio in a background task
    audio_url = generate_tts(response_text, session_id)

    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response_text
            },
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": "1",
                            "url": audio_url,
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ],
            "shouldEndSession": False
        }
    }

# Serve static audio files (for TTS)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=TTS_AUDIO_DIR), name="audio")
