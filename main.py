import os
import datetime
import subprocess
import speech_recognition as sr
import pyttsx3
import torch
import whisper
import numpy as np
from fuzzywuzzy import process
from Jarvis.features.calendar import authenticate_google, get_events
from Jarvis.features.youtube import youtube_search
from Jarvis.features.system import system_stats
from Jarvis.features.email import send_email
from Jarvis.llm import ask_llm

# Load Whisper Model
model = whisper.load_model("medium", device="cpu")

# Initialize Speech Recognition & TTS
recognizer = sr.Recognizer()
recognizer.energy_threshold = 100
recognizer.dynamic_energy_threshold = True
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

# Predefined Commands
COMMANDS = ["calendar", "email", "youtube", "system stats", "take a note", "who are you", "shutdown"]

def speak(text):
    """Speaks the given text synchronously."""
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    """Uses Whisper for speech recognition synchronously."""
    with sr.Microphone(sample_rate=16000) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for command...")
        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
            print("Processing speech...")
            
            # Convert audio to NumPy array with correct format
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0

            if audio_data is None or len(audio_data) == 0:
                speak("I couldn't process the audio. Please try again.")
                return None

            result = model.transcribe(audio_data, language="en", fp16=torch.cuda.is_available())

            if "text" not in result or not result["text"].strip():
                speak("I couldn't understand. Please repeat.")
                return None

            command = result["text"].strip().lower()
            print(f"User: {command}")

            # Match against predefined commands
            command_match, score = process.extractOne(command, COMMANDS) if command else (None, 0)
            if command_match and score > 75:
                return command_match  # Return the matched command
            else:
                return command  # Return the raw user input (for note-taking)
        
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Try again.")
            return None
        except Exception as e:
            print(f"Error in command listening: {e}")
            speak("There was an issue processing your speech.")
            return None

def handle_command(command):
    """Handles recognized commands synchronously."""
    print(f"Processing command: {command}")
    if command == "calendar":
        service = authenticate_google()
        get_events(datetime.date.today(), service)
    elif command == "youtube":
        speak("What would you like to search on YouTube?")
        query = listen_for_command()
        if query:
            youtube_search(query)
    elif command == "email":
        handle_email()
    elif command == "system stats":
        speak(system_stats())
    elif command == "take a note":
        take_note()
    elif command == "who are you":
        speak("I am Jarvis, An AI assistant created by The smartest man alive King Nahal. I am here to help you with your tasks.")
    elif command == "shutdown":
        speak("Goodbye!")
        os._exit(0)
    else:
        response = ask_llm(command)
        speak(response)

def handle_email():
    """Handles voice-based email composition."""
    speak("Who is the recipient?")
    recipient = listen_for_command()
    if not recipient:
        speak("No recipient provided.")
        return

    speak("What is the subject?")
    subject = listen_for_command()
    if not subject:
        speak("No subject provided.")
        return

    speak("What is the message?")
    message = listen_for_command()
    if not message:
        speak("No message provided.")
        return

    response = send_email(recipient, subject, message)
    speak(response)

def take_note():
    """Handles voice-controlled note-taking."""
    speak("What should I write down?")
    note_text = listen_for_command()  # Only calls listen_for_command once

    if note_text:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"note_{timestamp}.txt"
        with open(filename, "w") as file:
            file.write(note_text)
        speak(f"I've saved the note: {note_text}")
        subprocess.Popen(["notepad", filename], close_fds=True)
    else:
        speak("No note was recorded.")

if __name__ == "__main__":
    speak("Jarvis is now online, Sir. How can I help you today Boss?")
    
    while True:
        command = listen_for_command()
        if command:
            handle_command(command)
