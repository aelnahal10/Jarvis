import re
import datetime
import pyttsx3
from Jarvis.features import calendar, wikipedia_search, website, weather, youtube, system, email, notes
from Jarvis.llm import ask_llm

class JarvisAssistant:
    def __init__(self):
        self.speaker = pyttsx3.init()

    def speak(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()
    
    def process_command(self, command):
        command = command.lower()
        
        if "calendar" in command:
            service = calendar.authenticate_google()
            date = calendar.get_date(command)
            calendar.get_events(date, service)
        
        elif "wikipedia" in command or "tell me about" in command:
            topic = command.replace("tell me about", "").strip()
            response = wikipedia_search.search(topic)
            self.speak(response)
        
        elif "weather" in command:
            city = command.split(" ")[-1]
            response = weather.fetch_weather(city)
            self.speak(response)
        
        elif "open" in command:
            domain = command.split("open ")[-1]
            website.website_opener(domain)
        
        elif "youtube" in command:
            youtube.youtube_search(command.replace("search youtube for", "").strip())
        
        elif "system stats" in command:
            response = system.system_stats()
            self.speak(response)
        
        elif "send email" in command:
            self.speak("Who should I send the email to?")
            recipient = input("Recipient: ")
            self.speak("What should the subject be?")
            subject = input("Subject: ")
            self.speak("What should the message say?")
            message = input("Message: ")
            email.send_email(recipient, subject, message)
            self.speak("Email sent successfully.")
        
        elif "take note" in command:
            self.speak("What should I note down?")
            text = input("Note: ")
            notes.note(text)
            self.speak("I have saved the note.")
        
        else:
            response = ask_llm(command)
            self.speak(response)
