"""Tests for the LLM service — prompt building only, no API calls."""

from app.services.llm_service import build_prompt, SYSTEM_PROMPT


class TestBuildPrompt:

    def test_includes_system_prompt(self):
        result = build_prompt("doc text", [])
        assert SYSTEM_PROMPT in result

    def test_includes_document_text(self):
        result = build_prompt("My important document content", [])
        assert "My important document content" in result
        assert "--- DOCUMENT CONTENT ---" in result
        assert "--- END DOCUMENT ---" in result

    def test_includes_conversation_history(self):
        history = [
            {"role": "user", "content": "What is this about?"},
            {"role": "assistant", "content": "It's about testing."},
            {"role": "user", "content": "Tell me more."},
        ]
        result = build_prompt("doc text", history)
        assert "User: What is this about?" in result
        assert "Assistant: It's about testing." in result
        assert "User: Tell me more." in result

    def test_ends_with_assistant_prefix(self):
        result = build_prompt("doc text", [{"role": "user", "content": "Hi"}])
        assert result.rstrip().endswith("Assistant:")

    def test_empty_history(self):
        result = build_prompt("doc text", [])
        assert "doc text" in result
        assert result.rstrip().endswith("Assistant:")