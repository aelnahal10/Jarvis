import speech_recognition as sr
import asyncio
import requests
from gtts import gTTS
from playsound import playsound
import os

# Initialize Recognizer
recognizer = sr.Recognizer()

# Hugging Face LLM API Configuration
LLM_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
LLM_API_KEY = "your_huggingface_api_key" 

# Directory for Temporary TTS Audio Files
AUDIO_DIR = "audio/"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Hotwords List
HOTWORDS = ["Hey jarvis", "jarvis", "hello jarvis", "yo jarvis"]

# Helper Functions
async def send_to_llm(query):
    """
    Sends the query to the Hugging Face LLM API and retrieves the response.
    """
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    payload = {"inputs": query}
    try:
        print("Sending query to LLM...")
        response = await asyncio.to_thread(requests.post, LLM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        generated_text = data.get("generated_text", "I'm not sure how to respond to that.")
        print(f"LLM Response: {generated_text}")
        return generated_text
    except Exception as e:
        print(f"Error connecting to LLM: {e}")
        return "Sorry, I couldn't process your request."

async def generate_tts(text, filename):
    """
    Converts text to speech and saves it as an audio file.
    """
    try:
        print("Generating TTS...")
        tts = gTTS(text)
        tts.save(filename)
        print(f"TTS saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None

async def play_audio(filename):
    """
    Plays the TTS audio response.
    """
    try:
        print("Playing response audio...")
        playsound(filename)
    except Exception as e:
        print(f"Error playing audio: {e}")

def detect_hotword(text):
    """
    Detects if the input text contains any of the defined hotwords.
    Returns the detected hotword and the query after it.
    """
    for hotword in HOTWORDS:
        if hotword in text.lower():
            # Extract query after the hotword
            query = text.lower().replace(hotword, "").strip()
            return hotword, query
    return None, None  # No hotword detected

async def listen_and_process():
    """
    Continuously listens for audio input, processes the query, and retrieves responses from LLM.
    """
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"Listening for hotwords: {HOTWORDS}...")

        while True:
            try:
                # Listen for audio
                print("Waiting for speech...")
                audio = await asyncio.to_thread(recognizer.listen, source, timeout=5)
                print("Audio captured, processing...")

                # Process the audio
                await process_audio(audio)

            except sr.WaitTimeoutError:
                print("No speech detected, continuing...")
            except Exception as e:
                print(f"Error while listening: {e}")

async def process_audio(audio):
    """
    Transcribes audio to text, detects hotwords, and sends queries to the LLM.
    """
    try:
        # Transcribe audio to text
        text = await asyncio.to_thread(recognizer.recognize_google, audio)
        print(f"You said: {text}")

        # Detect hotword
        hotword, query = detect_hotword(text)
        if hotword:
            print(f"Hotword '{hotword}' detected! Processing the query...")
            if query:
                # Send query to LLM and get response
                response = await send_to_llm(query)
                
                # Generate TTS response
                audio_filename = os.path.join(AUDIO_DIR, "response.mp3")
                await generate_tts(response, audio_filename)
                
                # Play the response audio
                await play_audio(audio_filename)
            else:
                print("No query detected after hotword.")
        
        elif "stop listening" in text.lower():
            print("Stopping the assistant...")
            raise KeyboardInterrupt  # Stop the loop gracefully

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

async def main():
    """
    Main function to run the always-on voice assistant.
    """
    try:
        await listen_and_process()
    except KeyboardInterrupt:
        print("\nVoice assistant stopped.")

if __name__ == "__main__":
    asyncio.run(main())
