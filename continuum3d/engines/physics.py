"""Core physics engines — Newton, energy, projectile, orbital, stress-strain, hydraulics."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import (PROJECTILE_DT, PROJECTILE_MAX_STEPS,
                                STRESS_STRAIN_POINTS, STRAIN_RANGE, YIELD_STRAIN, G)


def newtons_second_law(mass: float, acceleration: float):
    """Newton's Second Law with dual visualization. Returns (Figure, formula_md)."""
    force = mass * acceleration
    t = np.linspace(0, 10, 200)
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"F = {mass} \u00d7 {acceleration} = {force:.2f} N", "Velocity vs Time"),
    )
    m_range = np.linspace(0.1, mass * 2, 60)
    fig.add_trace(go.Scatter(x=m_range, y=m_range * acceleration, mode="lines", name="F = ma",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[mass], y=[force], mode="markers", name="Operating Point",
                             marker=dict(color="#ef4444", size=14, symbol="diamond")), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=acceleration * t, mode="lines", name="v = at",
                             line=dict(color="#22c55e", width=3)), row=1, col=2)
    fig.update_xaxes(title_text="Mass (kg)", row=1, col=1)
    fig.update_yaxes(title_text="Force (N)", row=1, col=1)
    fig.update_xaxes(title_text="Time (s)", row=1, col=2)
    fig.update_yaxes(title_text="Velocity (m/s)", row=1, col=2)
    fig.update_layout(height=400)
    fig = dark_layout(fig, f"Newton's Second Law \u2014 F = {force:.2f} N")
    formula = (
        f"**Newton's Second Law**\n\n"
        f"$$F = m \\cdot a = {mass} \\times {acceleration} = {force:.2f} \\text{{ N}}$$\n\n"
        f"**Velocity after 10s:** $v = at = {acceleration} \\times 10 = {acceleration * 10:.2f}$ m/s\n\n"
        f"**Distance after 10s:** $d = \\frac{{1}}{{2}}at^2 = {0.5 * acceleration * 100:.2f}$ m\n\n"
        f"**Momentum:** $p = mv = {mass * acceleration * 10:.2f}$ kg\u00b7m/s at t=10s"
    )
    return fig, formula


def energy_calculator(mass: float, height: float, velocity: float, gravity: float = 9.81):
    """Kinetic / Potential energy with stacked bar chart."""
    ke = 0.5 * mass * velocity ** 2
    pe = mass * gravity * height
    total = ke + pe
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Kinetic Energy", "Potential Energy", "Total Mechanical"],
        y=[ke, pe, total],
        marker_color=["#3b82f6", "#22c55e", "#a855f7"],
        text=[f"{ke:.2f} J", f"{pe:.2f} J", f"{total:.2f} J"],
        textposition="outside",
    ))
    fig.update_yaxes(title_text="Energy (Joules)")
    fig = dark_layout(fig, "Energy Distribution")
    fig.update_layout(height=400)
    formula = (
        f"**Kinetic Energy:** $KE = \\frac{{1}}{{2}}mv^2 = \\frac{{1}}{{2}}({mass})({velocity})^2 = {ke:.2f}$ J\n\n"
        f"**Potential Energy:** $PE = mgh = ({mass})({gravity})({height}) = {pe:.2f}$ J\n\n"
        f"**Total Mechanical Energy:** $E = KE + PE = {total:.2f}$ J\n\n"
        f"**Energy Conservation:** $KE + PE = \\text{{const}}$ (no friction)"
    )
    return fig, formula


def projectile_motion(v0: float, angle_deg: float, gravity: float, drag: float, h0: float):
    """Full projectile simulation with optional quadratic air resistance."""
    angle = math.radians(angle_deg)
    vx, vy = v0 * math.cos(angle), v0 * math.sin(angle)
    dt = PROJECTILE_DT
    xs, ys, ts = [0.0], [h0], [0.0]
    cx, cy, cvx, cvy, ct = 0.0, h0, vx, vy, 0.0

    while cy >= 0 and ct < PROJECTILE_MAX_STEPS:
        speed = math.sqrt(cvx ** 2 + cvy ** 2)
        cvx += -drag * speed * cvx * dt
        cvy += (-gravity - drag * speed * cvy) * dt
        cx += cvx * dt
        cy += cvy * dt
        ct += dt
        xs.append(cx)
        ys.append(max(cy, 0.0))
        ts.append(ct)

    xs, ys = np.array(xs), np.array(ys)
    peak_idx = np.argmax(ys)
    max_h, rng, flight = ys[peak_idx], xs[-1], ts[-1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Trajectory",
                             line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[rng / 2], y=[max_h], mode="markers+text", showlegend=False,
                             text=[f"H={max_h:.1f}m"], textposition="top center",
                             marker=dict(color="#22c55e", size=10)))
    fig.update_xaxes(title_text="Horizontal Distance (m)")
    fig.update_yaxes(title_text="Height (m)")
    fig = dark_layout(fig, f"Projectile \u2014 v\u2080={v0} m/s, \u03b8={angle_deg}\u00b0")
    fig.update_layout(height=450)

    formula = (
        f"**Initial Components:** $v_{{0x}} = {vx:.2f}$ m/s, $v_{{0y}} = {vy:.2f}$ m/s\n\n"
        f"**Max Height:** $H = {max_h:.2f}$ m\n\n"
        f"**Range:** $R = {rng:.2f}$ m\n\n"
        f"**Flight Time:** $T = {flight:.2f}$ s"
    )
    if drag > 0:
        formula += f"\n\n**Drag Coefficient:** $b = {drag}$ (quadratic drag model)"
    return fig, formula


def orbital_mechanics(mass_primary: float, body_radius: float, altitude: float):
    """Orbital velocity, period, and escape velocity with orbit visualization."""
    G_const = G
    r = body_radius + altitude
    v_orb = math.sqrt(G_const * mass_primary / r)
    period = 2 * math.pi * r / v_orb
    v_esc = math.sqrt(2) * v_orb

    theta = np.linspace(0, 2 * np.pi, 300)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=body_radius * np.cos(theta) / 1e6, y=body_radius * np.sin(theta) / 1e6,
                             fill="toself", name="Primary Body", line=dict(color="#f59e0b", width=2)))
    fig.add_trace(go.Scatter(x=r * np.cos(theta) / 1e6, y=r * np.sin(theta) / 1e6,
                             mode="lines", name="Orbit", line=dict(color="#3b82f6", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=[r / 1e6], y=[0], mode="markers", name="Satellite",
                             marker=dict(color="#ef4444", size=10)))
    fig.update_layout(xaxis=dict(title="\u00d710\u2076 m", gridcolor="#334155"),
                      yaxis=dict(title="\u00d710\u2076 m", gridcolor="#334155", scaleanchor="x"),
                      height=450)
    fig = dark_layout(fig, f"Orbital Mechanics \u2014 r = {r / 1e6:.2f} \u00d710\u2076 m")

    period_str = f"{period / 3600:.2f} hours" if period < 86400 else f"{period / 86400:.2f} days"
    formula = (
        f"$$v_{{orb}} = \\sqrt{{\\frac{{GM}}{{r}}}} = {v_orb:.2f} \\text{{ m/s}}$$\n\n"
        f"**Orbital Period:** $T = {period_str}$\n\n"
        f"**Escape Velocity:** $v_{{esc}} = {v_esc:.2f}$ m/s\n\n"
        f"**Altitude:** $h = {altitude / 1e3:.1f}$ km"
    )
    return fig, formula


def robot_arm_fk(lengths: list, angles: list):
    """Forward kinematics for a planar multi-link robot arm."""
    n = min(len(lengths), len(angles))
    cum_angle = 0.0
    px, py = [0.0], [0.0]
    for i in range(n):
        cum_angle += math.radians(angles[i])
        px.append(px[-1] + lengths[i] * math.cos(cum_angle))
        py.append(py[-1] + lengths[i] * math.sin(cum_angle))

    end_x, end_y = px[-1], py[-1]
    reach = math.sqrt(end_x ** 2 + end_y ** 2)
    max_reach = sum(lengths)

    fig = go.Figure()
    theta_c = np.linspace(0, 2 * math.pi, 200)
    fig.add_trace(go.Scatter(x=max_reach * np.cos(theta_c), y=max_reach * np.sin(theta_c),
                             mode="lines", name="Max Reach",
                             line=dict(color="#334155", width=1, dash="dot")))
    colors = ["#3b82f6", "#22c55e", "#a855f7", "#f59e0b", "#ef4444", "#06b6d4"]
    for i in range(n):
        fig.add_trace(go.Scatter(
            x=[px[i], px[i + 1]], y=[py[i], py[i + 1]],
            mode="lines+markers", name=f"Link {i + 1}",
            line=dict(color=colors[i % len(colors)], width=6),
            marker=dict(size=[8, 14], color=colors[i % len(colors)]),
        ))
    fig.update_layout(xaxis=dict(title="X (m)", scaleanchor="y"), yaxis=dict(title="Y (m)"), height=450)
    fig = dark_layout(fig, f"Robot Arm FK \u2014 End Effector: ({end_x:.3f}, {end_y:.3f}) m")

    angles_str = " + ".join(f"\u03b8{i + 1}={angles[i]}\u00b0" for i in range(n))
    formula = (
        f"$$x = \\sum L_i \\cos(\\theta_{{cum}}) = {end_x:.4f}$$\n\n"
        f"$$y = \\sum L_i \\sin(\\theta_{{cum}}) = {end_y:.4f}$$\n\n"
        f"**Reach:** {reach:.3f} m / {max_reach:.3f} m max\n\n"
        f"**Angles:** {angles_str}"
    )
    return fig, formula


def stress_strain_calc(youngs_pa: float, cross_area: float, orig_length: float, force_n: float):
    """Stress-strain analysis with elastic/plastic curve."""
    stress = force_n / cross_area
    strain = stress / youngs_pa
    elongation = strain * orig_length

    yield_strain = YIELD_STRAIN
    strains = np.linspace(0, STRAIN_RANGE, STRESS_STRAIN_POINTS)
    sigma = np.where(strains <= yield_strain,
                     youngs_pa * strains,
                     youngs_pa * yield_strain * np.exp(-2 * (strains - yield_strain)) + stress * 0.3)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strains * 100, y=sigma / 1e6, mode="lines", name="\u03c3-\u03b5 Curve",
                             line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[strain * 100], y=[stress / 1e6], mode="markers", name="Operating Point",
                             marker=dict(color="#ef4444", size=14, symbol="diamond")))
    fig.add_vline(x=yield_strain * 100, line=dict(color="#f59e0b", dash="dash", width=1),
                  annotation_text="Yield")
    fig.update_xaxes(title_text="Strain (%)")
    fig.update_yaxes(title_text="Stress (MPa)")
    fig = dark_layout(fig, "Stress-Strain Curve")
    fig.update_layout(height=420)

    safety = youngs_pa / stress if stress > 0 else float("inf")
    formula = (
        f"**Stress:** $\\sigma = \\frac{{F}}{{A}} = \\frac{{{force_n:.1f}}}{{{cross_area}}} = {stress / 1e6:.2f}$ MPa\n\n"
        f"**Strain:** $\\varepsilon = \\frac{{\\sigma}}{{E}} = {strain * 100:.4f}$%\n\n"
        f"**Elongation:** $\\Delta L = {elongation * 1000:.4f}$ mm\n\n"
        f"**Young's Modulus:** $E = {youngs_pa / 1e9:.2f}$ GPa\n\n"
        f"**Safety Factor:** {safety:.1f}\u00d7"
    )
    return fig, formula


def hydraulic_pressure(depth: float, density: float, area: float):
    """Hydrostatic pressure vs depth with force calculation."""
    g = 9.81
    pressure = density * g * depth
    force = pressure * area
    d = np.linspace(0, max(depth * 1.5, 10), 200)
    p = density * g * d
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d, y=p / 1000, mode="lines", name="P = \u03c1gh",
                             line=dict(color="#06b6d4", width=3), fill="tozeroy",
                             fillcolor="rgba(6,182,212,0.1)"))
    fig.add_trace(go.Scatter(x=[depth], y=[pressure / 1000], mode="markers", name="Current Depth",
                             marker=dict(color="#ef4444", size=12)))
    fig.update_xaxes(title_text="Depth (m)")
    fig.update_yaxes(title_text="Pressure (kPa)")
    fig = dark_layout(fig, f"Hydrostatic Pressure \u2014 P = {pressure / 1000:.1f} kPa at {depth} m")
    fig.update_layout(height=420)
    formula = (
        f"$$P = \\rho g h = {density} \\times {g} \\times {depth} = {pressure:.0f} \\text{{ Pa}} = {pressure / 1000:.1f} \\text{{ kPa}}$$\n\n"
        f"**Force on area {area} m\u00b2:** $F = PA = {force:.1f}$ N\n\n"
        f"**Total (incl. atm):** $P_{{total}} = 101325 + {pressure:.0f} = {101325 + pressure:.0f}$ Pa"
    )
    return fig, formula
