"""Beam deflection engine — Simply Supported, Cantilever, Fixed-Fixed."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout


def beam_deflection(beam_type: str, length: float, load: float, ei: float, load_pos: float):
    """Beam deflection and bending moment for Simply Supported / Cantilever / Fixed-Fixed."""
    x = np.linspace(0, length, 300)
    a = load_pos * length
    b = length - a

    if beam_type == "Cantilever":
        delta = np.where(x <= a, (load * x ** 2) / (6 * ei) * (3 * a - x),
                         (load * a ** 2) / (6 * ei) * (3 * x - a))
        max_d = (load * length ** 3) / (3 * ei) if length > 0 else 0
        label = "Cantilever Beam"
        formula_tex = (
            f"$$\\delta_{{max}} = \\frac{{PL^3}}{{3EI}} = {max_d:.6f} \\text{{ m}}$$\n\n"
            f"$$P = {load} \\text{{ N}},\\; L = {length} \\text{{ m}},\\; EI = {ei} \\text{{ N\u00b7m}}^2$$"
        )
    elif beam_type == "Fixed-Fixed":
        delta = np.zeros_like(x)
        for i, xi in enumerate(x):
            if xi <= a:
                delta[i] = (load * b ** 2 * xi ** 2) / (6 * ei * length ** 3) * (3 * a * length - (3 * a + b) * xi)
            else:
                rx = length - xi
                delta[i] = (load * a ** 2 * rx ** 2) / (6 * ei * length ** 3) * (3 * b * length - (3 * b + a) * rx)
        max_d = (load * a ** 3 * b ** 3) / (3 * ei * length ** 3) if length > 0 else 0
        label = "Fixed-Fixed Beam"
        formula_tex = (
            f"$$\\delta_{{max}} = \\frac{{Pa^3b^3}}{{3EIL^3}} = {max_d:.6f} \\text{{ m}}$$\n\n"
            f"$$P = {load} \\text{{ N}},\\; a = {a:.2f} \\text{{ m}},\\; b = {b:.2f} \\text{{ m}}$$"
        )
    else:
        delta = np.where(
            x <= a,
            (load * b * x) / (6 * ei * length) * (length ** 2 - b ** 2 - x ** 2),
            (load * a * (length - x)) / (6 * ei * length) * (2 * length * x - x ** 2 - a ** 2),
        )
        max_d = (load * b * (length ** 2 - b ** 2) ** 1.5) / (9 * np.sqrt(3) * ei * length) if length > 0 else 0
        label = "Simply Supported Beam"
        formula_tex = (
            f"$$\\delta_{{max}} \\approx {max_d:.6f} \\text{{ m}}$$\n\n"
            f"$$P = {load} \\text{{ N}},\\; L = {length} \\text{{ m}},\\; EI = {ei}\\text{{ N\u00b7m}}^2$$"
        )

    moment = np.gradient(delta, x) * ei
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Deflection Curve", "Bending Moment Diagram"))
    fig.add_trace(go.Scatter(x=x, y=-delta * 1000, mode="lines", name="Deflection",
                             line=dict(color="#3b82f6", width=3), fill="tozeroy",
                             fillcolor="rgba(59,130,246,0.1)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=moment, mode="lines", name="Moment",
                             line=dict(color="#ef4444", width=3)), row=1, col=2)
    fig.update_xaxes(title_text="Position (m)", row=1, col=1)
    fig.update_yaxes(title_text="Deflection (mm)", row=1, col=1)
    fig.update_xaxes(title_text="Position (m)", row=1, col=2)
    fig.update_yaxes(title_text="Moment (N\u00b7m)", row=1, col=2)
    fig.update_layout(height=420)
    fig = dark_layout(fig, f"{label} \u2014 \u03b4_max = {max_d * 1000:.4f} mm")
    return fig, formula_tex
