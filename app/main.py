import asyncio
import os
import subprocess
import webbrowser
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import redis
import requests

# Redis Configuration for Session Management
redis_client = redis.StrictRedis(host="localhost", port=6380, decode_responses=True)

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://api.openrouter.ai/v1/chat/completions"
OPENROUTER_API_KEY = "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"  

# Directory for Temporary TTS Audio Files
AUDIO_DIR = "audio/"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

# Hotwords
HOTWORDS = ["jarvis", "hey jarvis", "hello jarvis"]

# Helper Functions
async def send_to_llm(session_id, query):
    """
    Sends the query to OpenRouter and retrieves the response.
    Uses Redis to manage session history for contextual responses.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    # Retrieve session context from Redis
    session_context = redis_client.lrange(session_id, 0, -1) or []
    messages = [{"role": "assistant", "content": msg} if i % 2 else {"role": "user", "content": msg}
                for i, msg in enumerate(session_context)]
    messages.append({"role": "user", "content": query})

    payload = {
        "model": "gpt-4",
        "messages": messages,
        "temperature": 0.7,
    }

    try:
        print("Sending query to OpenRouter...")
        response = await asyncio.to_thread(requests.post, OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        generated_text = data["choices"][0]["message"]["content"]
        print(f"LLM Response: {generated_text}")

        # Update session context in Redis
        redis_client.rpush(session_id, query, generated_text)
        return generated_text
    except Exception as e:
        print(f"Error connecting to OpenRouter: {e}")
        return "Sorry, I couldn't process your request."


async def execute_command(command):
    """
    Dynamically execute advanced commands for a software engineer with Python-specific features:
    - Open IDEs
    - Manage Git repositories
    - Interact with GitHub
    - Run and create Python scripts
    - Install dependencies
    - Manage virtual environments
    - Execute Python code snippets
    """
    try:
        # GitHub Personal Access Token (Replace with your token)
        GITHUB_API_URL = "https://api.github.com"
        GITHUB_TOKEN = "your_github_token"  # Add your GitHub token here for authenticated requests
        GITHUB_HEADERS = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Open a URL
        if "open" in command and "http" in command:
            url = command.split("open")[-1].strip()
            print(f"Opening URL: {url}")
            webbrowser.open(url)

        # Open a file or folder
        elif "open file" in command:
            file_path = command.split("file")[-1].strip()
            print(f"Opening file: {file_path}")
            os.startfile(file_path)
        elif "open folder" in command:
            folder_path = command.split("folder")[-1].strip()
            print(f"Opening folder: {folder_path}")
            os.startfile(folder_path)

        # Open IDE
        elif "open vs code" in command or "open vscode" in command:
            print("Opening Visual Studio Code...")
            subprocess.run(["code"], shell=True)
        elif "open pycharm" in command:
            print("Opening PyCharm...")
            subprocess.run(["pycharm"], shell=True)

        # Run a Python script
        elif "run script" in command:
            script_path = command.split("script")[-1].strip()
            print(f"Running Python script: {script_path}")
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            print(f"Script Output: {result.stdout}")
            return result.stdout

        # Create a new Python file
        elif "create python file" in command:
            file_name = command.split("file")[-1].strip()
            if not file_name.endswith(".py"):
                file_name += ".py"
            with open(file_name, "w") as f:
                f.write("# New Python script\n\nif __name__ == '__main__':\n    print('Hello, Jarvis!')")
            print(f"Python file created: {file_name}")
            return f"Python file created: {file_name}"

        # Install Python dependencies
        elif "install package" in command:
            package_name = command.split("package")[-1].strip()
            print(f"Installing Python package: {package_name}")
            result = subprocess.run(["pip", "install", package_name], capture_output=True, text=True)
            print(f"Installation Output: {result.stdout}")
            return result.stdout

        # Manage virtual environments
        elif "create virtual environment" in command:
            env_name = command.split("environment")[-1].strip()
            print(f"Creating virtual environment: {env_name}")
            result = subprocess.run(["python", "-m", "venv", env_name], capture_output=True, text=True)
            print(f"Virtual Environment Creation Output: {result.stdout}")
            return f"Virtual environment '{env_name}' created."
        elif "activate virtual environment" in command:
            env_name = command.split("environment")[-1].strip()
            print(f"Activating virtual environment: {env_name}")
            activation_script = os.path.join(env_name, "Scripts", "activate") if os.name == "nt" else os.path.join(env_name, "bin", "activate")
            subprocess.run([activation_script], shell=True)
            return f"Virtual environment '{env_name}' activated."

        # GitHub commands
        elif "github create repo" in command:
            repo_name = command.split("repo")[-1].strip()
            print(f"Creating GitHub repository: {repo_name}")
            payload = {"name": repo_name, "private": False}  # Adjust privacy as needed
            response = requests.post(f"{GITHUB_API_URL}/user/repos", json=payload, headers=GITHUB_HEADERS)
            if response.status_code == 201:
                repo_url = response.json()["html_url"]
                print(f"Repository created: {repo_url}")
                return f"GitHub repository '{repo_name}' created successfully: {repo_url}"
            else:
                print(f"Failed to create repository: {response.json()}")
                return f"Error creating repository: {response.json()}"

        elif "github clone" in command:
            repo_url = command.split("clone")[-1].strip()
            print(f"Cloning GitHub repository: {repo_url}")
            result = subprocess.run(["git", "clone", repo_url], capture_output=True, text=True)
            print(f"Git Clone Output:\n{result.stdout}")
            return result.stdout

        elif "github delete repo" in command:
            repo_name = command.split("repo")[-1].strip()
            print(f"Deleting GitHub repository: {repo_name}")
            response = requests.delete(f"{GITHUB_API_URL}/repos/your_github_username/{repo_name}", headers=GITHUB_HEADERS)
            if response.status_code == 204:
                print(f"Repository '{repo_name}' deleted successfully.")
                return f"GitHub repository '{repo_name}' deleted successfully."
            else:
                print(f"Failed to delete repository: {response.json()}")
                return f"Error deleting repository: {response.json()}"

        # Git commands
        elif "git status" in command:
            print("Checking Git status...")
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            print(f"Git Status:\n{result.stdout}")
            return result.stdout
        elif "git pull" in command:
            print("Pulling latest changes...")
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            print(f"Git Pull Output:\n{result.stdout}")
            return result.stdout
        elif "git commit" in command:
            message = command.split("commit")[-1].strip().strip('"')
            print(f"Committing changes with message: {message}")
            result = subprocess.run(["git", "commit", "-am", message], capture_output=True, text=True)
            print(f"Git Commit Output:\n{result.stdout}")
            return result.stdout

        # Unknown command
        else:
            print(f"Command not recognized: {command}")
            return "I couldn't understand that command."

    except Exception as e:
        print(f"Error executing command: {e}")
        return f"Error: {e}"

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
    Plays the TTS audio response asynchronously.
    """
    try:
        print("Playing response audio...")
        await asyncio.to_thread(playsound, filename)
    except Exception as e:
        print(f"Error playing audio: {e}")

async def execute_command(command):
    """
    Executes terminal, browser, file operations, and advanced software engineering commands.
    """
    try:
        # Handle browser control
        if "open" in command and "http" in command:
            url = command.split("open")[-1].strip()
            print(f"Opening URL: {url}")
            webbrowser.open(url)

        # Handle terminal commands
        elif "run command" in command:
            shell_command = command.split("command")[-1].strip()
            print(f"Running terminal command: {shell_command}")
            result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
            print(f"Command Output: {result.stdout}")
            return result.stdout

        # Handle file and folder operations
        elif "open file" in command:
            file_path = command.split("file")[-1].strip()
            print(f"Opening file: {file_path}")
            os.startfile(file_path)
        elif "open folder" in command:
            folder_path = command.split("folder")[-1].strip()
            print(f"Opening folder: {folder_path}")
            os.startfile(folder_path)

        # Fallback for unknown commands
        else:
            print("Command not recognized.")
            return "I couldn't understand that command."
    except Exception as e:
        print(f"Error executing command: {e}")
        return f"Error: {e}"

async def process_audio(audio, session_id):
    """
    Processes the audio, identifies commands or queries, and executes them.
    """
    try:
        # Transcribe audio to text
        text = await asyncio.to_thread(recognizer.recognize_google, audio)
        print(f"You said: {text}")

        # Detect hotwords
        hotword_detected = any(hotword in text.lower() for hotword in HOTWORDS)
        if hotword_detected:
            # Process and execute command
            query = text.lower().replace("jarvis", "").strip()
            if any(keyword in query for keyword in ["open", "run", "create", "install"]):
                result = await execute_command(query)
            else:
                result = await send_to_llm(session_id, query)

            # Generate and play TTS response
            audio_filename = os.path.join(AUDIO_DIR, "response.mp3")
            await generate_tts(result, audio_filename)
            await play_audio(audio_filename)
        elif "stop listening" in text.lower():
            print("Stopping the assistant...")
            raise KeyboardInterrupt  # Stop gracefully
        else:
            print("No hotword detected, ignoring input.")
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

async def listen_and_process():
    """
    Continuously listens for audio input and processes it.
    """
    session_id = "user_session"
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"Listening for hotwords: {HOTWORDS}...")

        while True:
            try:
                print("Waiting for speech...")
                audio = await asyncio.to_thread(recognizer.listen, source, timeout=5)
                print("Audio captured, processing...")
                await process_audio(audio, session_id)
            except sr.WaitTimeoutError:
                print("No speech detected, continuing...")
            except KeyboardInterrupt:
                print("Stopping Jarvis...")
                break
            except Exception as e:
                print(f"Error while listening: {e}")

async def main():
    """
    Main entry point for the unified assistant.
    """
    try:
        await listen_and_process()
    except KeyboardInterrupt:
        print("\nAssistant stopped.")
        redis_client.delete("user_session")

if __name__ == "__main__":
    asyncio.run(main())
