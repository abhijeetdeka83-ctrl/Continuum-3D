"""Groq API client with fail-safe error handling."""
from continuum3d.config import GROQ_MODEL, GROQ_API_KEY

try:
    import groq as groq_lib
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

_groq_client = None


def get_groq_client():
    """Initialize Groq client once, with fail-safe error handling."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    if not GROQ_AVAILABLE or not GROQ_API_KEY:
        return None
    try:
        _groq_client = groq_lib.Client(api_key=GROQ_API_KEY)
        return _groq_client
    except Exception:
        _groq_client = None
        return None


def groq_query(prompt: str, system_msg: str = "You are an expert engineer and physicist.") -> str:
    """Query Groq API with graceful degradation on every failure mode."""
    client = get_groq_client()
    if client is None:
        hint = ""
        if not GROQ_AVAILABLE:
            hint = "The `groq` package is not installed. "
        elif not GROQ_API_KEY:
            hint = "Set the GROQ_API_KEY environment variable. "
        return (
            f"AI engine unavailable. {hint}"
            "The deterministic calculation engine is fully operational \u2014 "
            "all formulas and visualizations work without AI."
        )
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except groq_lib.RateLimitError:
        return "Rate limit reached. The Groq free tier has request limits \u2014 please wait a moment and retry."
    except groq_lib.AuthenticationError:
        return "Invalid GROQ_API_KEY. Please check your key at console.groq.com."
    except groq_lib.APIConnectionError:
        return "Cannot reach Groq API. Check your network connection."
    except groq_lib.APIStatusError as e:
        return f"Groq API error (status {e.status_code}): {e.message}"
    except Exception:
        return "AI explanation unavailable due to an unexpected error. All calculations still work."
