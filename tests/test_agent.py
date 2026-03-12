"""
Tests for src/agent.py
=======================
Covers the typed deps container, default prompt, and the agent factory cache.
No Ollama connection is required — agent instances are just configuration
objects and make no network calls on construction.
"""

from src.agent import DEFAULT_SYSTEM_PROMPT, AgentDeps, get_agent


class TestAgentDeps:
    def test_default_system_prompt_is_non_empty(self):
        assert isinstance(DEFAULT_SYSTEM_PROMPT, str)
        assert len(DEFAULT_SYSTEM_PROMPT) > 0

    def test_deps_fields_default_to_empty_strings(self):
        deps = AgentDeps()
        assert deps.system_prompt == ""
        assert deps.rag_context == ""

    def test_deps_stores_provided_values(self):
        deps = AgentDeps(system_prompt="You are a pirate.", rag_context="Argh, treasure!")
        assert deps.system_prompt == "You are a pirate."
        assert deps.rag_context == "Argh, treasure!"

    def test_deps_with_only_system_prompt(self):
        deps = AgentDeps(system_prompt="Focus on Python.")
        assert deps.system_prompt == "Focus on Python."
        assert deps.rag_context == ""

    def test_deps_with_only_rag_context(self):
        deps = AgentDeps(rag_context="Some retrieved text.")
        assert deps.system_prompt == ""
        assert deps.rag_context == "Some retrieved text."


class TestGetAgentCache:
    def test_same_model_id_returns_the_same_instance(self):
        agent_a = get_agent("llama3.1")
        agent_b = get_agent("llama3.1")
        assert agent_a is agent_b

    def test_different_model_ids_return_different_instances(self):
        agent_a = get_agent("llama3.1")
        agent_b = get_agent("phi3")
        assert agent_a is not agent_b

    def test_returned_agent_is_not_none(self):
        agent = get_agent("llama3.1")
        assert agent is not None

    def test_multiple_calls_with_same_model_do_not_grow_cache(self):
        """Cache should not add duplicate entries for the same model."""
        from src.agent import _agent_cache
        get_agent("test-model-cache")
        get_agent("test-model-cache")
        count = sum(1 for k in _agent_cache if k == "test-model-cache")
        assert count == 1
