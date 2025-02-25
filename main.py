from Jarvis.features.calendar import authenticate_google, get_events
from Jarvis.features.wikipedia_search import tell_me_about
from Jarvis.features.weather import fetch_weather
from Jarvis.features.youtube import youtube_search
from Jarvis.features.system import system_stats
from Jarvis.features.email import send_email
from Jarvis.features.website import website_opener
from Jarvis.llm import ask_llm
import datetime
import speech_recognition as sr
import pyttsx3
import json
from vosk import Model, KaldiRecognizer

# Initialize Speech Recognition and Text-to-Speech Engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# Load Vosk model for offline wake-word detection
vosk_model = Model("vosk-model-small-en-us-0.15")  # Ensure this folder exists
wake_recognizer = KaldiRecognizer(vosk_model, 16000)  # Model listens for wake word

def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

def wake_word_detection():
    """Listens passively for the wake word 'Hey Jarvis'."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening for 'Hey Jarvis'...")

        while True:
            audio = recognizer.listen(source)
            if wake_recognizer.AcceptWaveform(audio.get_wav_data()):
                result = json.loads(wake_recognizer.Result())
                text = result.get("text", "").lower()
                if "jarvis" in text:  # Wake word detected
                    speak("Yes? How can I assist?")
                    return listen_for_command()  # Switch to active command mode

def listen_for_command():
    """Listens for a user command after activation."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")

        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio).lower()
            print(f"User: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Can you repeat?")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is down.")
            return ""

def process_command(command):
    """Processes and executes user commands."""

    if "calendar" in command or "events" in command:
        service = authenticate_google()
        today = datetime.date.today()
        get_events(today, service)

    elif "weather" in command:
        city = command.split("weather in")[-1].strip()
        if city:
            response = fetch_weather(city)
            speak(response)
        else:
            speak("Please specify a city for the weather update.")

    elif "wikipedia" in command or "tell me about" in command:
        topic = command.replace("tell me about", "").strip()
        response = tell_me_about(topic)
        speak(response)

    elif "youtube" in command:
        search_query = command.replace("youtube", "").strip()
        youtube_search(search_query)

    elif "email" in command:
        speak("Who is the recipient?")
        recipient = listen_for_command()
        speak("What is the subject?")
        subject = listen_for_command()
        speak("What is the message?")
        message = listen_for_command()
        result = send_email(recipient, subject, message)
        speak(result)

    elif "open website" in command:
        domain = command.split("open website")[-1].strip()
        website_opener(domain)
        speak(f"Opening {domain}.")

    elif "system stats" in command or "status" in command:
        response = system_stats()
        speak(response)

    elif "who are you" in command or "what can you do" in command:
        response = "I am Jarvis, your AI assistant. I can check the weather, search the web, play music, and assist with various tasks."
        speak(response)

    elif "exit" in command or "goodbye" in command:
        speak("Shutting down. Goodbye!")
        exit()

    else:
        # If command is unknown, ask LLM for a response
        response = ask_llm(command)
        speak(response)

if __name__ == "__main__":
    speak("Jarvis AI is online. Say 'Hey Jarvis' to activate.")
    while True:
        user_command = wake_word_detection()  # Listens for wake word first
        if user_command:
            process_command(user_command)  # Process the command
