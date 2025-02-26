import os
import datetime
import subprocess
from Jarvis.features.calendar import authenticate_google, get_events
from Jarvis.features.youtube import youtube_search
from Jarvis.features.system import system_stats
from Jarvis.features.email import send_email
from Jarvis.llm import ask_llm
import speech_recognition as sr
import pyttsx3
import json
import time
from vosk import Model, KaldiRecognizer

# Initialize Speech Recognition and Text-to-Speech Engine
recognizer = sr.Recognizer()
# Initialize Speech Recognition and Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Slightly faster than 180, you can adjust this number
engine.setProperty('volume', 0.9)

# Load Vosk model for offline wake-word detection
vosk_model = Model("vosk-model") 
wake_recognizer = KaldiRecognizer(vosk_model, 16000)  # Model listens for wake word

# Variable to store the last time the wake word was detected
last_wake_time = None
WAKE_WORD_INTERVAL = 300  # 5 minutes in seconds

def speak(text):
    """Converts text to speech."""
    print(f"Speaking: {text}")  # Debugging line
    engine.say(text)
    engine.runAndWait()

def take_note():
    """Takes a note and opens it in Notepad++."""
    speak("What should I write down?")
    note_text = listen_for_command()

    if note_text:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"note_{timestamp}.txt"

        with open(filename, "w") as file:
            file.write(note_text)

        speak("I've made a note.")
        
        # Open the note with Notepad++ if available
        notepad_path = "C://Program Files (x86)//Notepad++//notepad++.exe"
        if os.path.exists(notepad_path):
            subprocess.Popen([notepad_path, filename])
        else:
            speak("Notepad++ is not installed, opening with default text editor.")
            os.system(f"notepad {filename}")

def listen_for_wake_word():
    """Listens for the wake word 'Hey Jarvis'."""
    global last_wake_time
    current_time = time.time()

    # Check if it's been more than 5 minutes since the last wake word detection
    if last_wake_time and current_time - last_wake_time < WAKE_WORD_INTERVAL:
        return False

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Sleeping...Say Hey Jarvis to wake me up.")

        try:
            audio = recognizer.listen(source, timeout=10)
            if wake_recognizer.AcceptWaveform(audio.get_raw_data()):
                print("Wake word detected!")
                last_wake_time = current_time  # Update the last wake word detection time
                return True
            else:
                return False
        except sr.UnknownValueError:
            return False
        except sr.RequestError:
            speak("Speech recognition service is down.")
            return False

def listen_for_command():
    """Listens for a user command after activation."""
    with sr.Microphone() as source:
        speak("Listening...")

        try:
            audio = recognizer.listen(source, timeout=5)  # Reduce timeout time
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
    """Processes and executes user commands with LLM fallback for general queries."""
    print(f"Processing command: {command}")  # Debugging line

    # 🔹 Hardcoded (direct execution) commands
    if "calendar" in command or "events" in command:
        service = authenticate_google()
        today = datetime.date.today()
        get_events(today, service)

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

    elif "system stats" in command or "status" in command:
        response = system_stats()
        speak(response)

    elif "take a note" in command or "write this down" in command or "remember this" in command:
        take_note()

    elif "who are you" in command or "what can you do" in command:
        response = "I am Jarvis, your AI assistant. I can check the weather, search the web, play music, and assist with various tasks."
        speak(response)

    elif "You can rest now" in command or "That's it Thanks" in command:
        speak("Okay sir, Shutting down now. Goodbye!")
        exit()

    else:
        response = ask_llm(command)
        speak(response)

def main_loop():
    """Main loop that listens for wake word and handles user commands."""
    while True:
        if listen_for_wake_word():  # Detect wake word (only after 5 minutes)
            speak("How can I assist you?")
            user_command = listen_for_command()  # Once the wake word is detected, listen for command
            if user_command:
                process_command(user_command)  # Process the command
            else:
                speak("Sorry, I didn't catch your command.")

            # After processing the command, continue to check for the wake word only after 5 minutes
            speak("Listening for wake word...")  # Ready to listen again after completing the task.

if __name__ == "__main__":
    speak("Jarvis AI is online. Say 'Hey Jarvis' to activate.")
    main_loop()
