import anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, LLM_REQUEST_TIMEOUT_SECONDS


def get_llm_client():
    """Get a configured Anthropic client."""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_llm(prompt: str, system: str = None, max_tokens: int = 4096,
             temperature: float = 0.7) -> dict:
    """Make a single LLM call and return structured result.

    Args:
        prompt: The user message content.
        system: Optional system prompt.
        max_tokens: Maximum response tokens.
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative).

    Returns:
        {
            'success': bool,
            'content': str,        # The response text
            'usage': dict,         # Token usage stats
            'error': Optional[str]
        }
    """
    try:
        client = get_llm_client()
        kwargs = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs, timeout=LLM_REQUEST_TIMEOUT_SECONDS)

        return {
            "success": True,
            "content": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "usage": None,
            "error": str(e)
        }
