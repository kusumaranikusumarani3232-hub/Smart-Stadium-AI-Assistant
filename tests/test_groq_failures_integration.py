"""
tests/test_groq_failures_integration.py
========================================
Integration and component-level tests for Groq API failure handling.
Verifies that the application's AI features (chat, decision support, alerts, reports)
gracefully handle rate limits, auth errors, model-not-found, and missing client scenarios.
"""
import pytest
from unittest.mock import MagicMock, patch
from utils.groq_client import chat_completion, is_api_available

def _make_faulty_client(exception_msg: str) -> MagicMock:
    """Helper to build a mock Groq client that raises an exception when calling create()."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception(exception_msg)
    return mock_client

class TestGroqIntegrationFailures:
    """Verifies workflow error outcomes when calling chat_completion under API failures."""

    def test_missing_api_key_degradation(self):
        """When GROQ_API_KEY is not set or empty, chat_completion must return a helpful notice."""
        with patch("utils.groq_client.get_groq_client", return_value=None):
            result = chat_completion([{"role": "user", "content": "Test"}])
        assert "AI service unavailable" in result or "GROQ_API_KEY" in result

    def test_rate_limit_handling_in_decision_support(self):
        """If a rate limit occurs, chat_completion returns a specific user-friendly error message."""
        faulty_client = _make_faulty_client("rate_limit exceeded on server")
        with patch("utils.groq_client.get_groq_client", return_value=faulty_client):
            # Simulate a Crowd Monitoring decision support prompt call
            result = chat_completion([{"role": "system", "content": "You are operations AI"},
                                      {"role": "user", "content": "Analyze crowd"}])
        
        assert "Rate limit reached" in result
        assert "try again" in result

    def test_invalid_api_key_handling_in_incident_report(self):
        """If an invalid API key is provided, the return message guides the user to check settings."""
        faulty_client = _make_faulty_client("invalid_api_key or authentication failure")
        with patch("utils.groq_client.get_groq_client", return_value=faulty_client):
            # Simulate Incident Report generation call
            result = chat_completion([{"role": "user", "content": "Generate report"}])
        
        assert "Invalid API key" in result
        assert "check your groq_api_key" in result.lower()

    def test_model_not_found_handling_in_multilingual_assistant(self):
        """If the requested model is not found, the error returns details and fallback tips."""
        faulty_client = _make_faulty_client("model_not_found: llama-3.3-not-exists")
        with patch("utils.groq_client.get_groq_client", return_value=faulty_client):
            # Simulate Multilingual chat call
            result = chat_completion([{"role": "user", "content": "Hello"}], model="llama-3.3-not-exists")
        
        assert "Model not found" in result
        assert "llama-3.1-8b-instant" in result

    def test_generic_api_error_in_admin_panel(self):
        """If a generic exception occurs, it returns the error string gracefully without crashing."""
        faulty_client = _make_faulty_client("unknown system outage")
        with patch("utils.groq_client.get_groq_client", return_value=faulty_client):
            # Simulate Admin Panel alert generation call
            result = chat_completion([{"role": "user", "content": "Generate alerts"}])
        
        assert "AI error" in result
        assert "unknown system outage" in result
