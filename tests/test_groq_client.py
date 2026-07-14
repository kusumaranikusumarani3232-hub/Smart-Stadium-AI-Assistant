"""
tests/test_groq_client.py
=========================
Unit tests for utils/groq_client.py

The Groq API is NEVER called in these tests.
All network calls are intercepted by pytest-mock / unittest.mock.

Two layers of mocking are used:
  1. `get_groq_client()` — patched to return a mock client with controlled
     `chat.completions.create()` behaviour.
  2. `st.secrets` — patched via `monkeypatch` so the module can be imported
     without a real Streamlit runtime.
"""
import pytest
from unittest.mock import MagicMock, patch


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_mock_client(response_text: str = "Mock AI response") -> MagicMock:
    """Build a mock Groq client whose completions return response_text."""
    mock_choice = MagicMock()
    mock_choice.message.content = response_text

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


# ── chat_completion — happy path ───────────────────────────────────────────────

class TestChatCompletionSuccess:
    """Tests for the normal (successful) execution path of chat_completion()."""

    def test_returns_response_text(self):
        """When the client returns a valid response, chat_completion echoes the text."""
        from utils.groq_client import chat_completion

        mock_client = _make_mock_client("Hello from the stadium AI!")
        with patch("utils.groq_client.get_groq_client", return_value=mock_client):
            result = chat_completion([{"role": "user", "content": "Hi"}])

        assert result == "Hello from the stadium AI!"

    def test_calls_create_with_correct_model(self):
        """The model parameter must be forwarded to client.chat.completions.create."""
        from utils.groq_client import chat_completion

        mock_client = _make_mock_client()
        with patch("utils.groq_client.get_groq_client", return_value=mock_client):
            chat_completion(
                [{"role": "user", "content": "test"}],
                model="llama-3.3-70b-versatile",
            )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("model") == "llama-3.3-70b-versatile"

    def test_calls_create_with_correct_max_tokens(self):
        """max_tokens parameter must be forwarded."""
        from utils.groq_client import chat_completion

        mock_client = _make_mock_client()
        with patch("utils.groq_client.get_groq_client", return_value=mock_client):
            chat_completion(
                [{"role": "user", "content": "test"}],
                max_tokens=256,
            )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("max_tokens") == 256

    def test_calls_create_with_correct_temperature(self):
        """temperature parameter must be forwarded."""
        from utils.groq_client import chat_completion

        mock_client = _make_mock_client()
        with patch("utils.groq_client.get_groq_client", return_value=mock_client):
            chat_completion(
                [{"role": "user", "content": "test"}],
                temperature=0.2,
            )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("temperature") == pytest.approx(0.2)


# ── chat_completion — client unavailable ──────────────────────────────────────

class TestChatCompletionNoClient:
    """When get_groq_client() returns None, a user-friendly warning must be returned."""

    def test_returns_warning_string(self):
        from utils.groq_client import chat_completion

        with patch("utils.groq_client.get_groq_client", return_value=None):
            result = chat_completion([{"role": "user", "content": "Hello"}])

        # Must be a string (not an exception, not None)
        assert isinstance(result, str)
        # Must contain actionable guidance
        assert "GROQ_API_KEY" in result or "unavailable" in result.lower()

    def test_no_api_call_made_when_no_client(self):
        """If client is None, create() must never be called."""
        from utils.groq_client import chat_completion

        mock_client = _make_mock_client()
        with patch("utils.groq_client.get_groq_client", return_value=None):
            chat_completion([{"role": "user", "content": "Hello"}])

        mock_client.chat.completions.create.assert_not_called()


# ── chat_completion — API error handling ──────────────────────────────────────

class TestChatCompletionErrors:
    """Tests for specific error-case branches in chat_completion()."""

    def _run_with_exception(self, exc_message: str) -> str:
        """Helper: run chat_completion with a client that raises an exception."""
        from utils.groq_client import chat_completion

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception(exc_message)
        with patch("utils.groq_client.get_groq_client", return_value=mock_client):
            return chat_completion([{"role": "user", "content": "test"}])

    def test_rate_limit_error_message(self):
        result = self._run_with_exception("rate_limit exceeded")
        assert "rate limit" in result.lower() or "Rate limit" in result

    def test_invalid_api_key_error_message(self):
        result = self._run_with_exception("invalid_api_key provided")
        assert "API key" in result or "api key" in result.lower()

    def test_authentication_error_message(self):
        result = self._run_with_exception("authentication failed")
        assert "API key" in result or "api key" in result.lower()

    def test_model_not_found_error_message(self):
        result = self._run_with_exception("model_not_found: xyz")
        assert "Model not found" in result or "model" in result.lower()

    def test_generic_error_returns_string(self):
        result = self._run_with_exception("some unexpected error occurred")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_error_returns_are_strings(self):
        """All error paths must return a string, never raise."""
        error_msgs = [
            "rate_limit exceeded",
            "invalid_api_key",
            "authentication failure",
            "model_not_found",
            "connection reset by peer",
        ]
        from utils.groq_client import chat_completion

        for msg in error_msgs:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception(msg)
            with patch("utils.groq_client.get_groq_client", return_value=mock_client):
                result = chat_completion([{"role": "user", "content": "test"}])
            assert isinstance(result, str), f"Non-string result for error: {msg!r}"


# ── is_api_available ───────────────────────────────────────────────────────────

class TestIsApiAvailable:
    """Tests for is_api_available() — checks secrets without a real Streamlit session."""

    def test_returns_false_when_exception_raised(self):
        """If st.secrets raises (no Streamlit runtime), return False gracefully."""
        from utils.groq_client import is_api_available

        with patch("utils.groq_client.st") as mock_st:
            mock_st.secrets.get.side_effect = Exception("no runtime")
            result = is_api_available()

        assert result is False

    def test_returns_false_for_empty_key(self):
        from utils.groq_client import is_api_available

        with patch("utils.groq_client.st") as mock_st:
            mock_st.secrets.get.return_value = ""
            result = is_api_available()

        assert result is False

    def test_returns_false_for_short_key(self):
        """Keys shorter than 10 characters must be treated as invalid."""
        from utils.groq_client import is_api_available

        with patch("utils.groq_client.st") as mock_st:
            mock_st.secrets.get.return_value = "short"
            result = is_api_available()

        assert result is False

    def test_returns_true_for_valid_length_key(self):
        from utils.groq_client import is_api_available

        with patch("utils.groq_client.st") as mock_st:
            mock_st.secrets.get.return_value = "gsk_" + "x" * 40
            result = is_api_available()

        assert result is True
