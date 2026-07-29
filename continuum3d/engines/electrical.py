"""Electrical engineering engines — DC/AC circuits, RLC, Bode plots."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_MEDIUM


def dc_circuit(v_s: float, r1: float, r2: float, r3: float):
    """DC circuit analysis — series, parallel, voltage divider."""
    r_series = r1 + r2 + r3
    i_series = v_s / r_series if r_series > 0 else 0
    v_drops = [i_series * r for r in [r1, r2, r3]]

    r_par = 1 / (1 / r1 + 1 / r2 + 1 / r3) if all(r > 0 for r in [r1, r2, r3]) else 0
    i_par = v_s / r_par if r_par > 0 else 0
    i_branches = [v_s / r for r in [r1, r2, r3]]

    labels = ["R1", "R2", "R3"]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Series Current", "Parallel Currents"))
    fig.add_trace(go.Bar(x=labels, y=v_drops, name="Voltage Drop (V)",
                         marker_color=["#3b82f6", "#22c55e", "#f59e0b"]), row=1, col=1)
    fig.add_trace(go.Bar(x=labels, y=i_branches, name="Branch Current (A)",
                         marker_color=["#3b82f6", "#22c55e", "#f59e0b"]), row=1, col=2)
    fig.update_xaxes(title_text="Component", row=1, col=1)
    fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
    fig.update_xaxes(title_text="Component", row=1, col=2)
    fig.update_yaxes(title_text="Current (A)", row=1, col=2)
    fig = dark_layout(fig, f"DC Circuit — V_s = {v_s} V")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Series:** R_eq = {r_series:.1f} Ω | I = {i_series:.3f} A\n\n"
        f"**Voltage Drops:** {', '.join(f'{v:.2f}V' for v in v_drops)}\n\n"
        f"**Parallel:** R_eq = {r_par:.2f} Ω | I_total = {i_par:.3f} A\n\n"
        f"**Branch Currents:** {', '.join(f'{i:.3f}A' for i in i_branches)}"
    )
    return fig, formula


def rlc_circuit(r: float, l: float, c: float, v_ac: float, f_start: float, f_end: float):
    """RLC circuit — impedance, resonance, Bode magnitude/phase."""
    f = np.logspace(math.log10(f_start), math.log10(f_end), 500)
    w = 2 * math.pi * f
    z = np.sqrt(r ** 2 + (w * l - 1 / (w * c)) ** 2)
    phi = np.arctan2(w * l - 1 / (w * c), r)
    i = v_ac / z
    fn = 1 / (2 * math.pi * math.sqrt(l * c)) if l > 0 and c > 0 else 0
    zn = r

    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=("Bode Magnitude (Impedance)", "Bode Phase"),
                        specs=[[{"type": "xy"}], [{"type": "xy"}]])
    fig.add_trace(go.Scatter(x=f, y=z, mode="lines", name="|Z|",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[fn], y=[zn], mode="markers",
                             name=f"Resonance {fn:.1f} Hz",
                             marker=dict(color="#ef4444", size=10)), row=1, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Impedance (Ω)", type="log", row=1, col=1)
    fig.add_trace(go.Scatter(x=f, y=np.degrees(phi), mode="lines", name="Phase",
                             line=dict(color="#22c55e", width=3)), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="#475569", width=1), row=2, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", type="log", row=2, col=1)
    fig.update_yaxes(title_text="Phase (°)", row=2, col=1)
    fig = dark_layout(fig, f"RLC Circuit — f_n = {fn:.1f} Hz")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Resonant Frequency:** f_n = 1/(2π√(LC)) = {fn:.1f} Hz\n\n"
        f"**Impedance at Resonance:** Z = R = {zn:.2f} Ω\n\n"
        f"**L:** {l:.4f} H | **C:** {c:.6e} F | **R:** {r:.2f} Ω\n\n"
        f"**At f={f_start:.0f} Hz:** Z={z[0]:.1f} Ω, φ={np.degrees(phi[0]):.1f}°\n\n"
        f"**At f={f_end:.0f} Hz:** Z={z[-1]:.1f} Ω, φ={np.degrees(phi[-1]):.1f}°"
    )
    return fig, formula
