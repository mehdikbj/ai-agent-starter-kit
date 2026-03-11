import os
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

import src.config 

# 1. Initialize the Local Model
model = OpenAIChatModel(os.getenv("MODEL_ID", "llama3.1"))

# 2. Define the Developer's Default Prompt
# C'est ce texte qui s'affichera par défaut dans l'interface de l'utilisateur
DEFAULT_SYSTEM_PROMPT = (
    "You are a Senior AI Engineer Assistant. "
    "Your goal is to help developers build AI apps locally using Ollama. "
    "Keep your answers technical, concise, and provide Markdown code snippets."
)

# 3. Define the AI Agent
agent = Agent(model, deps_type=str)

# 4. Dynamic System Prompt
@agent.system_prompt
def add_dynamic_prompt(ctx: RunContext[str]) -> str:
    # Si l'interface web envoie un texte, on l'utilise. 
    # Sinon (par sécurité), on utilise le prompt par défaut.
    return ctx.deps if ctx.deps else DEFAULT_SYSTEM_PROMPT