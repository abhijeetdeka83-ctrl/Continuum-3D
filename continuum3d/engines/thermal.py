"""Thermal engineering engines — Conduction, Convection, Radiation."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_MEDIUM


def heat_conduction(length: float, area: float, k: float, t_hot: float, t_cold: float):
    """1D Fourier conduction — temperature gradient and heat flux."""
    dx = length
    q = k * area * (t_hot - t_cold) / dx if dx > 0 else 0
    x = np.linspace(0, length, 200)
    t_line = t_hot - (t_hot - t_cold) * x / length

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x * 1000, y=t_line, mode="lines", name="Temperature",
                             fill="tozeroy", line=dict(color="#ef4444", width=3)))
    fig.update_xaxes(title_text="Position (mm)")
    fig.update_yaxes(title_text="Temperature (\u00b0C)")
    fig = dark_layout(fig, f"1D Conduction — Q = {q / 1000:.2f} kW")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Fourier's Law:** $Q = kA\\frac{{\\Delta T}}{{L}}$\n\n"
        f"**Heat Transfer Rate:** Q = {q:.2f} W ({q / 1000:.2f} kW)\n\n"
        f"**Temp Gradient:** {(t_hot - t_cold) / length / 1000:.2f} °C/mm\n\n"
        f"**k:** {k:.1f} W/m·K | **A:** {area:.4f} m² | **L:** {length * 1000:.0f} mm"
    )
    return fig, formula


def heat_convection(h: float, area: float, t_surface: float, t_ambient: float):
    """Convective heat transfer — Newton's law of cooling."""
    q = h * area * (t_surface - t_ambient)
    t_range = np.linspace(min(t_surface, t_ambient) - 10, max(t_surface, t_ambient) + 10, 300)
    q_range = h * area * (t_range - t_ambient)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_range, y=q_range / 1000, mode="lines", name="Q vs T_surface",
                             line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[t_surface], y=[q / 1000], mode="markers+text",
                             name=f"Operating: {q / 1000:.1f} kW",
                             text=[f"{q / 1000:.1f} kW"],
                             marker=dict(color="#ef4444", size=12)))
    fig.update_xaxes(title_text="Surface Temperature (\u00b0C)")
    fig.update_yaxes(title_text="Heat Transfer Rate (kW)")
    fig = dark_layout(fig, f"Convection — Q = hA(T_s\u2212T_\u221e)")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Newton's Law of Cooling:** Q = hA(T_s − T_∞)\n\n"
        f"**Heat Transfer Rate:** Q = {q:.2f} W ({q / 1000:.2f} kW)\n\n"
        f"**h:** {h:.1f} W/m²·K | **A:** {area:.4f} m²\n\n"
        f"**T_surface:** {t_surface:.1f} °C | **T_∞:** {t_ambient:.1f} °C\n\n"
        f"**ΔT:** {t_surface - t_ambient:.1f} °C"
    )
    return fig, formula


def heat_radiation(emissivity: float, area: float, t_surface: float, t_surr: float):
    """Radiative heat transfer — Stefan-Boltzmann law."""
    sigma = 5.670374419e-8
    ts_k = t_surface + 273.15
    tsr_k = t_surr + 273.15
    q = emissivity * sigma * area * (ts_k ** 4 - tsr_k ** 4)

    t_plot = np.linspace(0, max(t_surface, 500), 300)
    tk_plot = t_plot + 273.15
    q_plot = emissivity * sigma * area * (tk_plot ** 4 - tsr_k ** 4)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_plot, y=q_plot / 1000, mode="lines", name="Q vs T_surface",
                             line=dict(color="#f59e0b", width=3)))
    fig.add_trace(go.Scatter(x=[t_surface], y=[q / 1000], mode="markers+text",
                             name=f"Operating: {q / 1000:.1f} kW",
                             text=[f"{q / 1000:.1f} kW"],
                             marker=dict(color="#ef4444", size=12)))
    fig.update_xaxes(title_text="Surface Temperature (\u00b0C)")
    fig.update_yaxes(title_text="Radiative Heat Transfer (kW)")
    fig = dark_layout(fig, "Radiation — Stefan-Boltzmann Law")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Stefan-Boltzmann:** Q = εσA(T_s⁴ − T_surr⁴)\n\n"
        f"**Heat Transfer Rate:** Q = {q:.2f} W ({q / 1000:.2f} kW)\n\n"
        f"**ε:** {emissivity:.3f} | **A:** {area:.4f} m²\n\n"
        f"**T_surface:** {ts_k:.1f} K | **T_surr:** {tsr_k:.1f} K"
    )
    return fig, formula
