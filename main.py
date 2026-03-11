import asyncio
import os
from dotenv import load_dotenv

# 1. Configuration & Environment
load_dotenv()

# Force OpenAI SDK to point to local Ollama
os.environ["OPENAI_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
os.environ["OPENAI_API_KEY"] = "ollama"

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# 2. Initialize the Model
model = OpenAIChatModel(os.getenv("MODEL_ID", "llama3.1"))

# 3. Agent Definition
agent = Agent(
    model,
    system_prompt=(
        "You are a Senior AI Engineer Assistant. "
        "Your goal is to help developers build AI apps locally using Ollama. "
        "Keep your answers technical, concise, and provide Markdown code snippets."
    ),
)

async def chat():
    console.print(Panel(
        "[bold cyan]Ollama AI Starter Kit[/bold cyan]\n"
        "[italic]Local execution - No API costs[/italic]", 
        expand=False
    ))
    
    while True:
        try:
            user_input = console.input("[bold magenta]User > [/bold magenta]")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Shutting down agent... Goodbye![/yellow]")
                break

            with Live(Panel("Thinking...", title="Local LLM", border_style="cyan"), 
                      console=console, 
                      refresh_per_second=10) as live:
                
                # Le RAG / Streaming corrigé :
                async with agent.run_stream(user_input) as result:
                    # stream_text() renvoie le texte complet généré à l'instant T
                    async for full_text_so_far in result.stream_text():
                        live.update(
                            Panel(Markdown(full_text_so_far), 
                                  title="Agent Response", 
                                  border_style="cyan")
                        )
                        
        except Exception as e:
            console.print(f"[bold red]Critical Error:[/bold red] Is Ollama running? ({e})")
            break

if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")