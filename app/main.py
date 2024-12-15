import asyncio
import os
import subprocess
import webbrowser
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import redis
import requests

# Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6380
OPENROUTER_API_URL = "https://api.openrouter.ai/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
AUDIO_DIR = "audio/"
HOTWORDS = ["jarvis", "hey jarvis", "hello jarvis"]
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Redis and Speech Recognizer
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
recognizer = sr.Recognizer()

# Helper Functions
def get_abs_path(path):
    return os.path.abspath(path) if not os.path.isabs(path) else path

def check_file_exists(path):
    return os.path.exists(path)

def handle_error(e):
    print(f"Error: {e}")
    return f"Error: {e}"

async def send_to_llm(session_id, query):
    """Communicates with OpenRouter API."""
    try:
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        session_context = redis_client.lrange(session_id, 0, -1) or []
        messages = [
            {"role": "assistant" if i % 2 else "user", "content": msg}
            for i, msg in enumerate(session_context)
        ]
        messages.append({"role": "user", "content": query})

        payload = {"model": "gpt-4", "messages": messages, "temperature": 0.7}
        response = await asyncio.to_thread(requests.post, OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        generated_text = response.json()["choices"][0]["message"]["content"]

        redis_client.rpush(session_id, query, generated_text)
        return generated_text
    except Exception as e:
        return handle_error(e)

async def execute_command(command):
    """Executes commands related to files, folders, URLs, IDEs, GitHub, virtual environments, and Python scripts."""
    try:
        if "open" in command:
            target = command.split("open")[-1].strip()
            if target.startswith("http"):
                webbrowser.open(target)
                return f"URL '{target}' opened."
            path = get_abs_path(target)
            if check_file_exists(path):
                os.startfile(path)
                return f"Opened '{path}'."
            return f"Error: '{target}' does not exist."

        elif "run script" in command:
            script_path = get_abs_path(command.split("script")[-1].strip())
            if check_file_exists(script_path):
                result = subprocess.run(["python", script_path], capture_output=True, text=True)
                return result.stdout
            return f"Error: Script '{script_path}' does not exist."

        elif "install package" in command:
            package_name = command.split("package")[-1].strip()
            result = subprocess.run(["pip", "install", package_name], capture_output=True, text=True)
            return result.stdout

        elif "create python file" in command:
            file_name = command.split("file")[-1].strip()
            file_path = os.path.join(os.getcwd(), file_name if file_name.endswith(".py") else f"{file_name}.py")
            if check_file_exists(file_path):
                return f"File '{file_name}' already exists."
            with open(file_path, "w") as f:
                f.write("# New Python script\n\nif __name__ == '__main__':\n    print('Hello, Jarvis!')")
            return f"Python file created: {file_path}"

        elif "create virtual environment" in command:
            env_name = command.split("environment")[-1].strip()
            env_path = os.path.join(os.getcwd(), env_name)
            subprocess.run(["python", "-m", "venv", env_path], check=True)
            return f"Virtual environment '{env_name}' created at {env_path}."

        elif "activate virtual environment" in command:
            env_name = command.split("environment")[-1].strip()
            activation_script = os.path.join(env_name, "Scripts", "activate") if os.name == "nt" else os.path.join(env_name, "bin", "activate")
            if check_file_exists(activation_script):
                subprocess.run([activation_script], shell=True)
                return f"Virtual environment '{env_name}' activated."
            return f"Error: Virtual environment '{env_name}' does not exist."

        elif "github create repo" in command:
            repo_name = command.split("repo")[-1].strip()
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            payload = {"name": repo_name, "private": False}
            response = requests.post(f"{GITHUB_API_URL}/user/repos", json=payload, headers=headers)
            if response.status_code == 201:
                return f"GitHub repository '{repo_name}' created successfully: {response.json()['html_url']}"
            return f"Error creating repository: {response.json()}"

        elif "github clone" in command:
            repo_url = command.split("clone")[-1].strip()
            result = subprocess.run(["git", "clone", repo_url], capture_output=True, text=True)
            return result.stdout

        elif "github delete repo" in command:
            repo_name = command.split("repo")[-1].strip()
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            response = requests.delete(f"{GITHUB_API_URL}/repos/your_github_username/{repo_name}", headers=headers)
            if response.status_code == 204:
                return f"GitHub repository '{repo_name}' deleted successfully."
            return f"Error deleting repository: {response.json()}"

        elif "git" in command:
            git_command = command.split("git")[-1].strip()
            result = subprocess.run(["git"] + git_command.split(), capture_output=True, text=True)
            return result.stdout

        elif "git status" in command:
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            return result.stdout

        elif "git pull" in command:
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            return result.stdout

        elif "git commit" in command:
            message = command.split("commit")[-1].strip().strip('"')
            result = subprocess.run(["git", "commit", "-am", message], capture_output=True, text=True)
            return result.stdout

        elif "define python function" in command:
            function_name = command.split("function")[-1].strip()
            file_path = "current_file.py"
            function_definition = f"def {function_name}():\n    pass\n"

            if not check_file_exists(file_path):
                with open(file_path, "w") as f:
                    f.write("# Python functions\n\n")

            with open(file_path, "r") as f:
                if function_definition in f.read():
                    return f"Function '{function_name}' already exists in file: {file_path}"

            with open(file_path, "a") as f:
                f.write(f"\n{function_definition}")
            return f"Function '{function_name}' defined in file: {file_path}"

        elif "add python imports" in command:
            imports = command.split("imports")[-1].strip()
            file_path = "current_file.py"
            import_statement = f"{imports}\n"

            if not check_file_exists(file_path):
                with open(file_path, "w") as f:
                    f.write("# Python import statements\n\n")

            with open(file_path, "r") as f:
                if import_statement in f.read():
                    return f"Import '{imports}' already exists in file: {file_path}"

            with open(file_path, "a") as f:
                f.write(import_statement)
            return f"Imports added to file: {file_path}"

        return "Command not recognized."
    except Exception as e:
        return handle_error(e)


async def generate_tts(text):
    """Generates text-to-speech audio."""
    try:
        filename = os.path.join(AUDIO_DIR, "response.mp3")
        tts = gTTS(text)
        tts.save(filename)
        return filename
    except Exception as e:
        return handle_error(e)

async def play_audio(filename):
    """Plays audio file."""
    try:
        await asyncio.to_thread(playsound, filename)
    except Exception as e:
        handle_error(e)

async def process_audio(audio, session_id):
    """Processes audio input, identifies commands, and executes them."""
    try:
        text = await asyncio.to_thread(recognizer.recognize_google, audio)
        print(f"You said: {text}")

        if any(hotword in text.lower() for hotword in HOTWORDS):
            query = text.lower().replace("jarvis", "").strip()
            result = await execute_command(query) if any(
                keyword in query for keyword in ["open", "run", "create", "install", "github", "git"]
            ) else await send_to_llm(session_id, query)

            audio_file = await generate_tts(result)
            if audio_file:
                await play_audio(audio_file)
        elif "stop listening" in text.lower():
            print("Stopping the assistant...")
            raise KeyboardInterrupt
        else:
            print("No hotword detected, ignoring input.")
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
    except Exception as e:
        handle_error(e)

async def listen_and_process():
    """Continuously listens for audio input and processes it."""
    session_id = "user_session"
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"Listening for hotwords: {HOTWORDS}...")

        while True:
            try:
                audio = await asyncio.to_thread(recognizer.listen, source, timeout=5)
                await process_audio(audio, session_id)
            except sr.WaitTimeoutError:
                pass
            except KeyboardInterrupt:
                print("Stopping Jarvis...")
                redis_client.delete(session_id)
                break
            except Exception as e:
                handle_error(e)

async def main():
    try:
        await listen_and_process()
    except KeyboardInterrupt:
        print("Assistant stopped.")

if __name__ == "__main__":
    asyncio.run(main())
