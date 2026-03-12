"""
Agent Module
============
Defines the PydanticAI agent, its typed dependencies, tools, and system prompt.

To add a new tool, define a function inside `_build_agent` decorated with
`@new_agent.tool_plain` (no RunContext needed) or `@new_agent.tool` (receives
RunContext as first arg, giving access to deps and the model settings).
"""

import os
from dataclasses import dataclass
from datetime import datetime

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel

import src.config  # Applies the Ollama bridge config on import


@dataclass
class AgentDeps:
    """
    Typed dependency container injected into the agent at runtime.
    Decouples UI state from the agent definition and makes tool/prompt
    logic fully testable without Streamlit.
    """
    system_prompt: str = ""
    rag_context: str = ""  # Populated by the RAG module when docs are uploaded


DEFAULT_SYSTEM_PROMPT = (
    "You are a Senior AI Engineer Assistant. "
    "Your goal is to help developers build AI apps locally using Ollama. "
    "Keep your answers technical, concise, and provide Markdown code snippets."
)


_agent_cache: dict[str, Agent] = {}


def get_agent(model_id: str) -> Agent:
    """Returns a fully-configured, cached Agent for the given Ollama model ID."""
    if model_id not in _agent_cache:
        _agent_cache[model_id] = _build_agent(model_id)
    return _agent_cache[model_id]


def _build_agent(model_id: str) -> Agent:
    new_agent = Agent(
        OpenAIChatModel(model_id),
        deps_type=AgentDeps,
    )

    # --- Dynamic system prompt ---
    @new_agent.system_prompt
    def add_dynamic_prompt(ctx: RunContext[AgentDeps]) -> str:
        prompt = ctx.deps.system_prompt or DEFAULT_SYSTEM_PROMPT
        if ctx.deps.rag_context:
            prompt += (
                "\n\n## Retrieved Document Context\n"
                "The following excerpts were retrieved from the user's uploaded documents. "
                "Use them to answer the question when relevant. "
                "Always cite the source filename and page number.\n\n"
                + ctx.deps.rag_context
            )
        return prompt

    # --- Tool: current date/time ---
    @new_agent.tool_plain
    def get_current_datetime() -> str:
        """Returns the current date and time. Call this when the user asks what time or date it is."""
        return datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S")

    return new_agent


# Default agent — kept for backward compatibility with direct imports
agent = get_agent(os.getenv("MODEL_ID", "llama3.1"))