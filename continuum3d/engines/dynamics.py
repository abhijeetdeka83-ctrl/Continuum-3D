"""Dynamics engines — Vibration analysis, Fatigue analysis."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_MEDIUM


def vibration_sdof(mass: float, stiffness: float, damping_ratio: float,
                   f0: float, f_max: float, force_amp: float = 100):
    """SDOF vibration — natural frequency, resonance, time/frequency response."""
    wn = math.sqrt(stiffness / mass) if mass > 0 else 0
    fn_hz = wn / (2 * math.pi)
    cc = 2 * mass * wn
    c = damping_ratio * cc
    wd = wn * math.sqrt(1 - damping_ratio ** 2) if damping_ratio < 1 else 0

    f = np.linspace(f0, f_max, 500)
    w = 2 * math.pi * f
    h = 1 / np.sqrt((1 - (w / wn) ** 2) ** 2 + (2 * damping_ratio * w / wn) ** 2)
    phi = -np.arctan2(2 * damping_ratio * w / wn, 1 - (w / wn) ** 2)

    wn_idx = np.argmin(np.abs(w - wn))
    h_peak = h[wn_idx]
    f_peak = f[wn_idx] if wn_idx < len(f) else 0

    t = np.linspace(0, 2, 1000)
    if damping_ratio < 1:
        envelope = np.exp(-damping_ratio * wn * t)
        x_t = envelope * (np.sin(wd * t)) / (mass * wd)
    else:
        x_t = np.zeros_like(t)

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Frequency Response", "Impulse Response"),
                        specs=[[{"type": "xy"}, {"type": "xy"}]])
    fig.add_trace(go.Scatter(x=f, y=h, mode="lines", name="FRF",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[f_peak], y=[h_peak], mode="markers",
                             name=f"Resonance {f_peak:.1f} Hz",
                             marker=dict(color="#ef4444", size=12)), row=1, col=1)
    fig.add_hline(y=1 / math.sqrt(2), line=dict(color="#f59e0b", dash="dash", width=1),
                  row=1, col=1, annotation_text="-3dB")
    fig.update_xaxes(title_text="Frequency (Hz)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude Ratio", row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=x_t * 1e3, mode="lines", name="Response",
                             line=dict(color="#22c55e", width=3)), row=1, col=2)
    fig.update_xaxes(title_text="Time (s)", row=1, col=2)
    fig.update_yaxes(title_text="Displacement (mm)", row=1, col=2)
    fig = dark_layout(fig, f"SDOF Vibration — f_n = {fn_hz:.2f} Hz")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Natural Frequency:** ω_n = {wn:.2f} rad/s | f_n = {fn_hz:.2f} Hz\n\n"
        f"**Damped Frequency:** ω_d = {wd:.2f} rad/s (ζ={damping_ratio:.3f})\n\n"
        f"**Critical Damping:** c_c = {cc:.2f} N·s/m | **Actual:** c = {c:.2f}\n\n"
        f"**Resonance Peak:** {h_peak:.2f} × at {f_peak:.1f} Hz\n\n"
        f"**m:** {mass:.2f} kg | **k:** {stiffness:.1f} N/m"
    )
    if damping_ratio >= 1:
        formula += "\n\n*Overdamped system — no oscillation*"
    return fig, formula


def fatigue_sn(endurance_limit: float, uts: float, fatigue_exponent: float = -0.1,
               cycles_to_test: float = 10000):
    """S-N fatigue curve with Miner's cumulative damage."""
    n = np.logspace(0, 8, 500)
    s_n = np.where(n <= 1e3, uts * (1 + (endurance_limit / uts - 1) * np.log(n) / np.log(1000)),
                   endurance_limit + (uts - endurance_limit) * (1000 / n) ** (-fatigue_exponent))

    stress_at_test = (endurance_limit + (uts - endurance_limit)
                      * (1000 / cycles_to_test) ** (-fatigue_exponent))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n, y=s_n / 1e6, mode="lines", name="S-N Curve",
                             line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[cycles_to_test], y=[stress_at_test / 1e6],
                             mode="markers+text", name="Test Point",
                             text=[f"{stress_at_test / 1e6:.1f} MPa"],
                             textposition="top left",
                             marker=dict(color="#ef4444", size=12)))
    fig.add_hline(y=endurance_limit / 1e6, line=dict(color="#22c55e", dash="dash", width=1),
                  annotation_text=f"Endurance {endurance_limit / 1e6:.1f} MPa")
    fig.update_xaxes(title_text="Cycles to Failure N", type="log")
    fig.update_yaxes(title_text="Stress Amplitude (MPa)")
    fig = dark_layout(fig, f"Fatigue S-N Curve — Endurance: {endurance_limit / 1e6:.1f} MPa")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Endurance Limit:** S_e = {endurance_limit / 1e6:.1f} MPa\n\n"
        f"**Ultimate Tensile Strength:** S_ut = {uts / 1e6:.1f} MPa\n\n"
        f"**Stress at N={cycles_to_test:.0f}:** {stress_at_test / 1e6:.2f} MPa\n\n"
        f"**Fatigue Exponent:** b = {fatigue_exponent:.2f}\n\n"
        f"**Lifetime Regimes:** Low-cycle (<10³) → High-cycle → Endurance (>10⁶)"
    )
    return fig, formula
