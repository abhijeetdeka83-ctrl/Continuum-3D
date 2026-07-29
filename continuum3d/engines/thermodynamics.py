"""Thermodynamics engines — Carnot cycle, ideal gas, Bernoulli's equation."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import R, STD_PRESSURE, THERMO_STEPS


def carnot_cycle(th_high: float, th_low: float):
    """Full Carnot cycle PV diagram with efficiency, work, and heat."""
    TH = th_high + 273.15
    TL = th_low + 273.15
    eta = 1 - TL / TH
    n = 1.0
    P1 = STD_PRESSURE
    V1 = n * R * TH / P1
    V2 = V1 * 1.8
    P2 = n * R * TH / V2
    gamma = 7 / 5
    V3 = V2 * (TH / TL) ** (1 / (gamma - 1))
    V4 = V1 * V3 / V2
    P4 = n * R * TL / V4

    steps = THERMO_STEPS

    def isotherm(Va, Vb, T):
        v = np.linspace(Va, Vb, steps)
        return v, n * R * T / v

    def adiabat(Va, Vb, Pa, Va_ref):
        v = np.linspace(Va, Vb, steps)
        return v, Pa * (Va_ref / v) ** gamma

    v12, p12 = isotherm(V1, V2, TH)
    v23, p23 = adiabat(V2, V3, P2, V2)
    v34, p34 = isotherm(V3, V4, TL)
    v41, p41 = adiabat(V4, V1, P4, V4)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v12 * 1e3, y=p12 / 1e3, mode="lines",
                             name=f"1\u21922 Isothermal ({th_high}\u00b0C)", line=dict(color="#ef4444", width=3)))
    fig.add_trace(go.Scatter(x=v23 * 1e3, y=p23 / 1e3, mode="lines",
                             name="2\u21923 Adiabatic Exp.", line=dict(color="#f59e0b", width=3)))
    fig.add_trace(go.Scatter(x=v34 * 1e3, y=p34 / 1e3, mode="lines",
                             name=f"3\u21924 Isothermal ({th_low}\u00b0C)", line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=v41 * 1e3, y=p41 / 1e3, mode="lines",
                             name="4\u21921 Adiabatic Comp.", line=dict(color="#a855f7", width=3)))
    fig.update_xaxes(title_text="Volume (\u00d710\u207b\u00b3 m\u00b3)")
    fig.update_yaxes(title_text="Pressure (kPa)")
    fig = dark_layout(fig, f"Carnot Cycle \u2014 \u03b7 = {eta * 100:.1f}%")
    fig.update_layout(height=450)

    Qin = n * R * TH * math.log(V2 / V1)
    Qout = n * R * TL * math.log(V3 / V4)
    W = Qin - Qout
    formula = (
        f"$$\\eta = 1 - \\frac{{T_L}}{{T_H}} = 1 - \\frac{{{TL:.1f}}}{{{TH:.1f}}} = {eta * 100:.1f}\\%$$\n\n"
        f"**Heat In:** $Q_H = {Qin:.1f}$ J | **Heat Out:** $Q_L = {Qout:.1f}$ J\n\n"
        f"**Work:** $W = Q_H - Q_L = {W:.1f}$ J"
    )
    return fig, formula


def bernoulli_calc(rho: float, v1: float, h1: float, p1: float, h2: float):
    """Bernoulli equation solver with velocity/pressure profiles."""
    g = 9.81
    total = p1 + 0.5 * rho * v1 ** 2 + rho * g * h1
    v2_sq = 2 * (total - p1 - rho * g * h2) / rho
    v2 = math.sqrt(max(v2_sq, 0))
    p2 = total - 0.5 * rho * v2 ** 2 - rho * g * h2

    pos = np.linspace(0, 10, 300)
    vel = v1 + (v2 - v1) * pos / 10
    prs = p1 + (p2 - p1) * pos / 10

    fig = make_subplots(rows=2, cols=1, subplot_titles=("Velocity", "Pressure"),
                        vertical_spacing=0.18)
    fig.add_trace(go.Scatter(x=pos, y=vel, mode="lines", name="Velocity",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=pos, y=prs / 1e3, mode="lines", name="Pressure",
                             line=dict(color="#ef4444", width=3)), row=2, col=1)
    fig.update_xaxes(title_text="Position (m)", row=2, col=1)
    fig.update_yaxes(title_text="v (m/s)", row=1, col=1)
    fig.update_yaxes(title_text="P (kPa)", row=2, col=1)
    fig.update_layout(height=500)
    fig = dark_layout(fig, "Bernoulli's Equation Along Pipe")

    formula = (
        f"$$P_1 + \\frac{{1}}{{2}}\\rho v_1^2 + \\rho g h_1 = P_2 + \\frac{{1}}{{2}}\\rho v_2^2 + \\rho g h_2$$\n\n"
        f"**State 1:** P={p1:.0f} Pa, v={v1:.2f} m/s, h={h1:.1f} m\n\n"
        f"**State 2:** P={p2:.0f} Pa, v={v2:.2f} m/s, h={h2:.1f} m\n\n"
        f"**Total Head:** $H = {total / (rho * g):.2f}$ m"
    )
    return fig, formula


def ideal_gas_calc(pressure: float, volume: float, temperature: float):
    """Ideal gas law with multi-temperature PV isotherms."""
    R = 8.314
    TK = temperature + 273.15
    if pressure <= 0:
        pressure = R * TK / volume
    elif volume <= 0:
        volume = R * TK / pressure
    elif temperature <= 0:
        TK = pressure * volume / R
        temperature = TK - 273.15
    n_mol = pressure * volume / (R * TK)

    fig = go.Figure()
    v_range = np.linspace(0.001, max(volume * 3, 0.01), 300)
    for dt, c, lw in [(-100, "#60a5fa", 1.5), (-50, "#38bdf8", 1.5),
                       (0, "#22c55e", 3), (+50, "#f59e0b", 1.5), (+100, "#ef4444", 1.5)]:
        t = TK + dt
        if t > 0:
            fig.add_trace(go.Scatter(x=v_range * 1e3, y=n_mol * R * t / v_range / 1e3,
                                     mode="lines", name=f"T={temperature + dt}\u00b0C",
                                     line=dict(color=c, width=lw)))
    fig.add_trace(go.Scatter(x=[volume * 1e3], y=[pressure / 1e3], mode="markers",
                             name="State", marker=dict(color="white", size=12, symbol="x")))
    fig.update_xaxes(title_text="Volume (\u00d710\u207b\u00b3 m\u00b3)")
    fig.update_yaxes(title_text="Pressure (kPa)")
    fig = dark_layout(fig, "Ideal Gas \u2014 PV = nRT")
    fig.update_layout(height=420)

    formula = (
        f"$$PV = nRT \\implies n = {n_mol:.4f} \\text{{ mol}}$$\n\n"
        f"**State:** P = {pressure:.0f} Pa, V = {volume:.6f} m\u00b3, T = {temperature}\u00b0C = {TK:.1f} K\n\n"
        f"**Molar volume at STP:** 22.414 L/mol"
    )
    return fig, formula
