from Jarvis.llm import ask_llm

def search(topic):
    """Fetches topic information using LLM."""
    return ask_llm(f"Tell me about {topic}")
