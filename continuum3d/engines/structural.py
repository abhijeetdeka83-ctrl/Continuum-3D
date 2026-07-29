"""Structural mechanics engines — Column buckling, Torsion of shafts."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_STANDARD


def column_buckling(end_condition: str, youngs: float, length: float,
                    i_min: float, area: float, yield_s: float):
    """Euler/Johnson column buckling — critical load vs slenderness ratio."""
    pi2_ei = (math.pi ** 2) * youngs * i_min
    if end_condition == "Pinned-Pinned":
        le = length
    elif end_condition == "Fixed-Fixed":
        le = length / 2
    elif end_condition == "Fixed-Free":
        le = length * 2
    else:
        le = length / math.sqrt(2)

    r_min = math.sqrt(i_min / area) if area > 0 else 0
    sr = le / r_min if r_min > 0 else float("inf")
    sr_limit = math.sqrt(2 * pi2_ei / (area * yield_s)) if area > 0 and yield_s > 0 else 0

    if sr >= sr_limit:
        p_cr = pi2_ei / (le ** 2)
        mode = "Euler"
    else:
        p_cr = yield_s * area * (1 - yield_s * area * (le ** 2) / (4 * pi2_ei))
        mode = "Johnson"

    sr_range = np.linspace(max(1, sr * 0.3), sr * 1.5, 300)
    euler_sr = math.sqrt(pi2_ei / (area * youngs)) if area > 0 else 1
    euler_sr_range = np.linspace(max(euler_sr, sr_range[0]), sr_range[-1], 200)
    p_euler = [pi2_ei / ((s * r_min) ** 2) if s * r_min > 0 else 0 for s in euler_sr_range]
    p_johnson = [yield_s * area * (1 - yield_s * area * (s * r_min) ** 2 / (4 * pi2_ei))
                 for s in sr_range if s * r_min <= le / 2]

    fig = go.Figure()
    if len(p_euler) > 0:
        fig.add_trace(go.Scatter(x=euler_sr_range, y=np.array(p_euler) / 1000,
                                 mode="lines", name="Euler", line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[sr], y=[p_cr / 1000], mode="markers",
                             name=f"Operating ({mode})", marker=dict(color="#ef4444", size=14)))
    fig.update_xaxes(title_text="Slenderness Ratio (L/r)")
    fig.update_yaxes(title_text="Critical Load (kN)")
    fig = dark_layout(fig, f"Column Buckling — P_cr = {p_cr / 1000:.2f} kN ({mode})")
    fig.update_layout(height=PLOT_HEIGHT_STANDARD)

    formula = (
        f"**End Condition:** {end_condition} (L_eff = {le:.2f} m)\n\n"
        f"**Slenderness Ratio:** L/r = {sr:.1f} | **Transition:** L/r = {sr_limit:.1f}\n\n"
        f"**Critical Load:** P_cr = {p_cr / 1000:.2f} kN ({mode} buckling)\n\n"
        f"**σ_cr:** {p_cr / area / 1e6:.2f} MPa | **Yield:** {yield_s / 1e6:.2f} MPa"
    )
    if sr >= sr_limit:
        formula += f"\n\n*Euler regime — slender column*"
    else:
        formula += f"\n\n*Johnson regime — intermediate column*"
    return fig, formula


def torsion_shaft(radius: float, torque: float, shear_mod: float, length: float):
    """Torsion of a circular shaft — shear stress, angle of twist, polar moment."""
    j = math.pi * radius ** 4 / 2
    tau_max = torque * radius / j if j > 0 else 0
    theta = torque * length / (shear_mod * j) if j > 0 else 0
    theta_deg = math.degrees(theta)
    r = np.linspace(0, radius, 200)
    tau_r = torque * r / j if j > 0 else np.zeros_like(r)

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Shear Stress Distribution", "Shaft Cross-Section"))
    fig.add_trace(go.Scatter(x=r * 1000, y=tau_r / 1e6, mode="lines",
                             name="τ(r)", fill="tozeroy",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.update_xaxes(title_text="Radius (mm)", row=1, col=1)
    fig.update_yaxes(title_text="Shear Stress (MPa)", row=1, col=1)

    theta_vals = np.linspace(0, 2 * math.pi, 100)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                             marker=dict(color="#3b82f6", size=8, symbol="circle")), row=1, col=2)
    fig.add_trace(go.Scatter(x=radius * np.cos(theta_vals) * 1000,
                             y=radius * np.sin(theta_vals) * 1000,
                             mode="lines", name="Section",
                             line=dict(color="#475569", width=2)), row=1, col=2)
    fig.update_xaxes(title_text="mm", row=1, col=2, scaleanchor="y")
    fig.update_yaxes(title_text="mm", row=1, col=2)
    fig = dark_layout(fig, f"Torsion — τ_max = {tau_max / 1e6:.2f} MPa, θ = {theta_deg:.4f}°")
    fig.update_layout(height=PLOT_HEIGHT_STANDARD)

    formula = (
        f"**Polar Moment of Inertia:** J = πr⁴/2 = {j:.6e} m⁴\n\n"
        f"**Max Shear Stress:** τ_max = Tr/J = {tau_max / 1e6:.2f} MPa\n\n"
        f"**Angle of Twist:** θ = TL/GJ = {theta_deg:.4f}° ({theta:.6f} rad)\n\n"
        f"**G:** {shear_mod / 1e9:.1f} GPa | **r:** {radius * 1000:.0f} mm"
    )
    return fig, formula
