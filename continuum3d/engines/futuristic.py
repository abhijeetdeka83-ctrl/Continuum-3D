"""Futuristic physics engines — Schwarzschild, special relativity, wormholes."""
import math
import numpy as np
import plotly.graph_objects as go
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import G, C, SOLAR_MASS


def schwarzschild_calc(mass_solar: float):
    """Schwarzschild radius, Hawking temperature, time dilation."""
    M = mass_solar * SOLAR_MASS
    rs = 2 * G * M / C ** 2
    area = 4 * math.pi * rs ** 2
    T_hawk = 1.227e23 / M

    r = np.linspace(rs * 1.01, rs * 20, 500)
    td = np.sqrt(1 - rs / r)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r / rs, y=td, mode="lines", name="Time Dilation Factor",
                             line=dict(color="#a855f7", width=3)))
    fig.add_vline(x=1, line=dict(color="#ef4444", width=2, dash="dash"),
                  annotation_text="Event Horizon (r = r_s)")
    fig.add_hline(y=1, line=dict(color="#475569", dash="dot"), annotation_text="Flat Spacetime")
    fig.update_xaxes(title_text="r / r_s")
    fig.update_yaxes(title_text="\u221a(1 \u2212 r_s/r)")
    fig = dark_layout(fig, f"Gravitational Time Dilation \u2014 {mass_solar} M\u2609")
    fig.update_layout(height=450)

    formula = (
        f"$$r_s = \\frac{{2GM}}{{c^2}} = {rs:.3e} \\text{{ m}} = {rs / 1e3:.2f} \\text{{ km}}$$\n\n"
        f"**Event Horizon Area:** $A = 4\\pi r_s^2 = {area:.3e}$ m\u00b2\n\n"
        f"**Hawking Temperature:** $T_H \\approx {T_hawk:.3e}$ K\n\n"
        f"**Schwarzschild Radius:** {rs / 1e3:.2f} km"
    )
    return fig, formula


def relativistic_calc(v_frac: float, rest_mass: float):
    """Special relativity: Lorentz factor, time dilation, length contraction."""
    gamma = 1 / math.sqrt(1 - v_frac ** 2)
    rel_mass = rest_mass * gamma
    ke_rel = (gamma - 1) * rest_mass * (3e8) ** 2

    vf = np.linspace(0, 0.999, 600)
    gm = np.minimum(1 / np.sqrt(1 - vf ** 2), 25)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vf, y=gm, mode="lines", name="\u03b3 (Lorentz Factor)",
                             line=dict(color="#06b6d4", width=3), fill="tozeroy",
                             fillcolor="rgba(6,182,212,0.1)"))
    fig.add_trace(go.Scatter(x=[v_frac], y=[min(gamma, 25)], mode="markers", name="Current",
                             marker=dict(color="#ef4444", size=14)))
    fig.update_xaxes(title_text="v / c")
    fig.update_yaxes(title_text="\u03b3 (Lorentz Factor)")
    fig = dark_layout(fig, f"Lorentz Factor \u2014 \u03b3 = {gamma:.4f}")
    fig.update_layout(height=450)

    ke_ev = ke_rel / 1.602e-19
    formula = (
        f"$$\\gamma = \\frac{{1}}{{\\sqrt{{1 - {v_frac}^2}}}} = {gamma:.6f}$$\n\n"
        f"**Time Dilation:** $\\Delta t = {gamma:.4f} \\times \\Delta t_0$\n\n"
        f"**Length Contraction:** $L = L_0 / {gamma:.4f} = {1 / gamma:.6f} L_0$\n\n"
        f"**Relativistic Mass:** $m = {gamma:.4f} \\times {rest_mass} = {rel_mass:.4f}$ kg\n\n"
        f"**Relativistic KE:** $E_k = {ke_rel:.3e}$ J = {ke_ev:.3e} eV"
    )
    return fig, formula


def wormhole_calc(radius: float, tidal: float):
    """Morris-Thorne traversable wormhole embedding diagram."""
    r = np.linspace(-10, 10, 500)
    embed = np.where(np.abs(r) > 0.5,
                     radius * np.arccosh(np.clip(np.abs(r) / radius + 1, 1.01, 100)),
                     0.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r, y=embed, mode="lines", name="Upper",
                             line=dict(color="#a855f7", width=3)))
    fig.add_trace(go.Scatter(x=r, y=-embed, mode="lines", name="Lower",
                             line=dict(color="#a855f7", width=3), showlegend=False))
    fig.add_vline(x=0, line=dict(color="#ef4444", width=2, dash="dash"),
                  annotation_text=f"Throat r\u2080={radius}")
    fig.update_xaxes(title_text="r (m)")
    fig.update_yaxes(title_text="z (embedding)")
    fig = dark_layout(fig, f"Morris-Thorne Wormhole \u2014 Throat: {radius} m")
    fig.update_layout(height=450)

    formula = (
        f"$$ds^2 = -c^2 dt^2 + \\frac{{dr^2}}{{1 - r_0/r}} + r^2 d\\Omega^2$$\n\n"
        f"**Throat:** $r_0 = {radius}$ m\n\n"
        f"**Tidal Acceleration:** $\\Delta a = {tidal:.2f}$ m/s\u00b2 (across 2m human)\n\n"
        f"**Embedding:** $z(r) = r_0 \\cosh^{{-1}}(r/r_0)$ (Flamm's paraboloid)"
    )
    return fig, formula
