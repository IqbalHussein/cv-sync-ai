import os
from google import genai


_client = None


def get_gemini_client() -> genai.Client:
    """
    Return a configured Gemini client using the environment API key.

    Uses a cached instance to avoid re-creating the client on every call.

    Returns:
        Configured genai.Client instance.

    Raises:
        RuntimeError: If GEMINI_API_KEY is not set in the environment.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
    _client = genai.Client(api_key=api_key)
    return _client
