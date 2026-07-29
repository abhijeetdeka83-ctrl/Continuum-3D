"""Fluid dynamics engines — Pipe flow, Reynolds number, Darcy-Weisbach."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_MEDIUM


def pipe_flow(flow_rate: float, diameter: float, length: float,
              density: float, viscosity: float, roughness: float = 0.0):
    """Pipe flow analysis — Reynolds number, friction factor, pressure drop."""
    area = math.pi * diameter ** 2 / 4
    velocity = flow_rate / area if area > 0 else 0
    re = density * velocity * diameter / viscosity if viscosity > 0 else 0

    if re < 2000:
        f = 64 / re if re > 0 else 0
        regime = "Laminar"
    elif re < 4000:
        f = 0.04
        regime = "Transition"
    else:
        if roughness > 0:
            f = 0.25 / (math.log10(roughness / (3.7 * diameter) + 5.74 / re ** 0.9)) ** 2
        else:
            f = 0.0791 / re ** 0.25
        regime = "Turbulent"

    dp = f * (length / diameter) * (density * velocity ** 2 / 2) if diameter > 0 else 0
    head_loss = dp / (density * 9.81) if density > 0 else 0
    pump_power = dp * flow_rate

    q_range = np.linspace(max(0.0001, flow_rate * 0.1), flow_rate * 2, 100)
    dp_range = []
    for q in q_range:
        v = q / area if area > 0 else 0
        re_q = density * v * diameter / viscosity if viscosity > 0 else 0
        if re_q < 2000:
            f_q = 64 / re_q if re_q > 0 else 0
        else:
            f_q = 0.0791 / re_q ** 0.25 if roughness == 0 else \
                0.25 / (math.log10(roughness / (3.7 * diameter) + 5.74 / re_q ** 0.9)) ** 2
        dp_range.append(f_q * (length / diameter) * (density * v ** 2 / 2) if diameter > 0 else 0)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("System Curve", "Velocity Profile"))
    fig.add_trace(go.Scatter(x=q_range * 1000, y=np.array(dp_range) / 1000, mode="lines",
                             name="ΔP vs Q", fill="tozeroy",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[flow_rate * 1000], y=[dp / 1000], mode="markers+text",
                             name="Operating Point", text=[f"{dp / 1000:.1f} kPa"],
                             marker=dict(color="#ef4444", size=12)), row=1, col=1)
    fig.update_xaxes(title_text="Flow Rate (L/s)", row=1, col=1)
    fig.update_yaxes(title_text="Pressure Drop (kPa)", row=1, col=1)

    r = np.linspace(-diameter / 2, diameter / 2, 100)
    v_profile = 2 * velocity * (1 - (2 * r / diameter) ** 2) if regime == "Laminar" else \
        velocity * (1 - (2 * r / diameter) ** 2) ** (1 / 7)
    fig.add_trace(go.Scatter(x=r * 1000, y=v_profile, mode="lines", name="v(r)",
                             fill="tozeroy", line=dict(color="#22c55e", width=3)), row=1, col=2)
    fig.update_xaxes(title_text="Radius (mm)", row=1, col=2)
    fig.update_yaxes(title_text="Velocity (m/s)", row=1, col=2)
    fig = dark_layout(fig, f"Pipe Flow — {regime}, Re = {re:.0f}")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Flow Regime:** {regime} | **Re:** {re:.0f}\n\n"
        f"**Velocity:** {velocity:.2f} m/s | **Friction f:** {f:.4f}\n\n"
        f"**Pressure Drop:** ΔP = {dp:.2f} Pa ({dp / 1000:.2f} kPa)\n\n"
        f"**Head Loss:** h_f = {head_loss:.2f} m | **Pump Power:** {pump_power:.2f} W\n\n"
        f"**D:** {diameter * 1000:.0f} mm | **L:** {length:.1f} m | **ρ:** {density} kg/m³"
    )
    return fig, formula


def moody_chart(reynolds: float, rel_roughness: float = 0.001):
    """Moody chart — friction factor vs Reynolds number."""
    re = np.logspace(1, 8, 1000)
    rough_vals = [0.0, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05]

    fig = go.Figure()
    for rr in rough_vals:
        f = np.zeros_like(re)
        for i, r in enumerate(re):
            if r < 2000:
                f[i] = 64 / r
            else:
                f[i] = 0.25 / (math.log10(rr / 3.7 + 5.74 / r ** 0.9)) ** 2 if rr > 0 else \
                    0.0791 / r ** 0.25
        label = f"ε/D = {rr}" if rr > 0 else "Smooth"
        fig.add_trace(go.Scatter(x=re, y=f, mode="lines", name=label,
                                 line=dict(width=2 if rr > 0 else 3)))

    re_pt = reynolds
    if re_pt < 2000:
        f_pt = 64 / re_pt if re_pt > 0 else 0
    else:
        f_pt = 0.25 / (math.log10(rel_roughness / 3.7 + 5.74 / re_pt ** 0.9)) ** 2 if rel_roughness > 0 else \
            0.0791 / re_pt ** 0.25

    fig.add_trace(go.Scatter(x=[re_pt], y=[f_pt], mode="markers", name="Operating",
                             marker=dict(color="#ef4444", size=14)))
    fig.add_vline(x=2000, line=dict(color="#f59e0b", dash="dash"),
                  annotation_text="Transition")
    fig.add_vline(x=4000, line=dict(color="#f59e0b", dash="dash"))
    fig.update_xaxes(title_text="Reynolds Number Re", type="log")
    fig.update_yaxes(title_text="Friction Factor f", type="log")
    fig = dark_layout(fig, "Moody Chart — Friction Factor")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Re:** {re_pt:.0f} | **ε/D:** {rel_roughness}\n\n"
        f"**Friction Factor:** f = {f_pt:.4f}\n\n"
        f"**Regime:** {'Laminar' if re_pt < 2000 else 'Turbulent' if re_pt > 4000 else 'Transition'}"
    )
    return fig, formula
