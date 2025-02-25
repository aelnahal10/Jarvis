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

# Initialize Speech Recognition and Text-to-Speech Engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for user input via microphone."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"User: {command}")
            return command
        except sr.UnknownValueError:
            return "I didn't catch that."
        except sr.RequestError:
            return "Sorry, there was an issue with speech recognition."

def process_command(command):
    """Processes and executes user commands."""

    if "calendar" in command or "events" in command:
        service = authenticate_google()
        today = datetime.date.today()
        get_events(today, service)

    elif "weather" in command:
        city = command.split("weather in")[-1].strip()
        response = fetch_weather(city)
        speak(response)

    elif "wikipedia" in command or "tell me about" in command:
        topic = command.replace("tell me about", "").strip()
        response = tell_me_about(topic)
        speak(response)

    elif "youtube" in command:
        search_query = command.replace("youtube", "").strip()
        youtube_search(search_query)

    elif "email" in command:
        speak("Who is the recipient?")
        recipient = listen()
        speak("What is the subject?")
        subject = listen()
        speak("What is the message?")
        message = listen()
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
    speak("Jarvis AI is online. How can I assist you?")
    
    while True:
        user_command = listen()
        process_command(user_command)
