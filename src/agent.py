import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

# Ensure the environment and local bridge are configured before anything else
import src.config 

# 1. Initialize the Local Model
# It defaults to 'llama3.1' but can be overridden in the .env file
model = OpenAIChatModel(os.getenv("MODEL_ID", "llama3.1"))

# 2. Define the AI Agent
# The system prompt gives the agent its persona and instructions for formatting output
agent = Agent(
    model,
    system_prompt=(
        "You are a Senior AI Engineer Assistant. "
        "Your goal is to help developers build AI apps locally using Ollama. "
        "Keep your answers technical, concise, and provide Markdown code snippets."
    ),
)