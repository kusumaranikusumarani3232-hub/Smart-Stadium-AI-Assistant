"""
Groq API client wrapper for Smart Stadium AI Assistant.

IMPORTANT: Only import and call these functions when genuine AI reasoning
is required (chat, report generation, decision support, AI alerts).
Do NOT call for dashboards, charts, navigation, or analytics.
"""
import streamlit as st


def get_groq_client():
    """
    Return a Groq client initialised from st.secrets.
    Returns None if key is missing (AI features gracefully degrade).
    """
    try:
        from groq import Groq  # lazy import — avoids import error if not installed
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key or len(api_key) < 10:
            return None
        return Groq(api_key=api_key)
    except Exception:
        return None


def chat_completion(
    messages: list,
    model: str = "llama3-8b-8192",
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat completion request to Groq.

    Args:
        messages   : List of {"role": str, "content": str} dicts.
        model      : Groq model ID.  Use 'llama-3.3-70b-versatile' for complex
                     reasoning; 'llama3-8b-8192' for fast real-time chat.
        temperature: Sampling temperature (0 = deterministic, 1 = creative).
        max_tokens : Upper token limit for the response.

    Returns:
        Response text string, or a user-friendly error message string.
    """
    client = get_groq_client()
    if client is None:
        return (
            "⚠️ **AI service unavailable.**  \n"
            "Add your `GROQ_API_KEY` to **Streamlit Secrets** "
            "(`.streamlit/secrets.toml` locally, or the Secrets panel on Streamlit Cloud) "
            "to enable AI features."
        )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as exc:
        err = str(exc).lower()
        if "rate_limit" in err:
            return "⚠️ **Rate limit reached.** Please wait a moment and try again."
        if "invalid_api_key" in err or "authentication" in err:
            return "⚠️ **Invalid API key.** Check your GROQ_API_KEY in Streamlit Secrets."
        if "model_not_found" in err:
            return f"⚠️ **Model not found.** Try switching to `llama3-8b-8192`. Error: {exc}"
        return f"⚠️ **AI error:** {exc}"


def is_api_available() -> bool:
    """Return True if a GROQ_API_KEY is configured."""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        return bool(key and len(key) > 10)
    except Exception:
        return False
