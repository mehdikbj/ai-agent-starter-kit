import os
from dotenv import load_dotenv

def setup_environment():
    """
    Load environment variables and configure the local Ollama bridge.
    This tricks the OpenAI SDK into routing requests to the local machine.
    """
    load_dotenv()
    
    # Force the OpenAI SDK to point to the local Mac instance
    os.environ["OPENAI_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    os.environ["OPENAI_API_KEY"] = "ollama"

# Execute the setup automatically when this module is imported
setup_environment()