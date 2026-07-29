"""Configuration constants and environment variables."""
import os

# --- App Configuration ---
APP_TITLE = "Continuum 3D"
APP_DESC = "Zero-Storage Interactive 3D Engineering Workspace & Generative CAD Studio"
SERVER_NAME = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "7860"))
GRADIO_SHARE = os.environ.get("GRADIO_SHARE", "False").lower() == "true"

# --- Groq AI ---
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_TEMPERATURE = float(os.environ.get("GROQ_TEMPERATURE", "0.7"))
GROQ_MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "1024"))

# --- Physics Constants ---
G = 6.674e-11
C = 3e8
SOLAR_MASS = 1.989e30
R = 8.314
STD_PRESSURE = 101325.0
STD_TEMP = 298.15

# --- Default Plot Dimensions ---
PLOT_HEIGHT_STANDARD = 400
PLOT_HEIGHT_MEDIUM = 450
PLOT_HEIGHT_LARGE = 500

# --- Simulation Defaults ---
PROJECTILE_DT = 0.005
PROJECTILE_MAX_STEPS = 2000
STRESS_STRAIN_POINTS = 300
STRAIN_RANGE = 0.25
YIELD_STRAIN = 0.002
BEAM_SAMPLES = 300
THERMO_STEPS = 200

# --- Theme ---
PRIMARY_HUE = os.environ.get("THEME_HUE", "blue")
SECONDARY_HUE = os.environ.get("THEME_SECONDARY", "slate")
NEUTRAL_HUE = os.environ.get("THEME_NEUTRAL", "zinc")

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
