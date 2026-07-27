"""Configuration constants and environment variables."""
import os

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
APP_TITLE = "Continuum 3D"
APP_DESC = "Zero-Storage Interactive 3D Engineering Workspace & Generative CAD Studio"

CSS = """
.status-bar {
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 20px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.main-title { font-size: 1.4em; font-weight: 700; color: #e2e8f0; }
.sub-text { color: #94a3b8; font-size: 0.85em; }
"""

HEADER_HTML = (
    '<div class="status-bar">'
    '<span class="main-title">Continuum 3D</span>'
    '<span class="sub-text">| Interactive 3D Engineering Workspace | '
    "\U0001f7e2 Ephemeral RAM Active \u2014 $0 Storage | "
    "Groq Llama 3.3 70B + Deterministic Engine</span></div>"
)
