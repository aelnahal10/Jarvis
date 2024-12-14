from gtts import gTTS
import os

def generate_tts(text: str, output_file: str) -> str:
    tts = gTTS(text)
    output_path = f"/tmp/{output_file}"
    tts.save(output_path)
    return output_path
