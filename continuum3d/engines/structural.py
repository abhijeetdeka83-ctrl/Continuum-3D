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


def beam_bending(span: float, load_p: float, load_pos: float, e_mod: float, i_moment: float):
    """Simply supported beam with point load — shear force & bending moment diagrams."""
    a = load_pos
    b = span - a
    ra = load_p * b / span
    rb = load_p * a / span
    x = np.linspace(0, span, 500)
    v = np.where(x <= a, ra, -rb)
    m = np.where(x <= a, ra * x, ra * x - load_p * (x - a))
    defl = np.zeros_like(x)
    for i, xi in enumerate(x):
        if xi <= a:
            defl[i] = load_p * b * xi * (span ** 2 - b ** 2 - xi ** 2) / (6 * e_mod * i_moment * span)
        else:
            xj = xi - a
            defl[i] = load_p * b * xi * (span ** 2 - b ** 2 - xi ** 2) / (6 * e_mod * i_moment * span) \
                      + load_p * (xj ** 3) / (6 * e_mod * i_moment)
    m_max = max(np.abs(m))
    v_max = max(np.abs(v))
    defl_max = max(np.abs(defl))

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Shear Force Diagram", "Bending Moment Diagram",
                                        "Deflection (Beam Theory)"),
                        vertical_spacing=0.06)
    fig.add_trace(go.Scatter(x=x, y=v / 1000, mode="lines", name="V(x)",
                             fill="tozeroy", line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_hline(y=0, line=dict(color="#475569", width=1), row=1, col=1)
    fig.update_yaxes(title_text="Shear Force (kN)", row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=m / 1000, mode="lines", name="M(x)",
                             fill="tozeroy", line=dict(color="#f59e0b", width=3)), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="#475569", width=1), row=2, col=1)
    fig.update_yaxes(title_text="Moment (kN·m)", row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=defl * 1000, mode="lines", name="δ(x)",
                             line=dict(color="#22c55e", width=3)), row=3, col=1)
    fig.update_xaxes(title_text="Span (m)", row=3, col=1)
    fig.update_yaxes(title_text="Deflection (mm)", row=3, col=1)
    fig = dark_layout(fig, f"Beam Bending — M_max = {m_max / 1000:.2f} kN·m, δ_max = {defl_max * 1000:.2f} mm")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Reactions:** R_A = {ra / 1000:.2f} kN, R_B = {rb / 1000:.2f} kN\n\n"
        f"**Max Shear:** V_max = {v_max / 1000:.2f} kN\n\n"
        f"**Max Moment:** M_max = {m_max / 1000:.2f} kN·m at x = {a:.2f} m\n\n"
        f"**Max Deflection:** δ_max = {defl_max * 1000:.2f} mm\n\n"
        f"**E:** {e_mod / 1e9:.1f} GPa | **I:** {i_moment:.6f} m⁴"
    )
    return fig, formula


def stress_strain(youngs: float, yield_s: float, uts: float, strain_max: float = 0.05):
    """Elastic-plastic stress-strain curve using Ramberg-Osgood approximation."""
    n = math.log(uts / yield_s) / math.log(0.2 / 0.002) if yield_s > 0 else 5
    strain = np.linspace(0, strain_max, 500)
    stress_elastic = youngs * strain
    stress_plastic = yield_s + (uts - yield_s) * np.tanh((strain - yield_s / youngs) * 20)
    stress = np.where(strain <= yield_s / youngs, stress_elastic, stress_plastic)
    stress[stress > uts * 1.05] = uts * 1.05

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strain * 100, y=stress / 1e6, mode="lines", name="σ-ε",
                             line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[yield_s / youngs * 100], y=[yield_s / 1e6],
                             mode="markers", name=f"Yield {yield_s / 1e6:.0f} MPa",
                             marker=dict(color="#ef4444", size=12)))
    fig.add_trace(go.Scatter(x=[strain[np.argmax(stress)] * 100], y=[uts / 1e6],
                             mode="markers", name=f"UTS {uts / 1e6:.0f} MPa",
                             marker=dict(color="#f59e0b", size=12)))
    fig.update_xaxes(title_text="Strain ε (%)")
    fig.update_yaxes(title_text="Stress σ (MPa)")
    fig = dark_layout(fig, f"Stress-Strain — E={youngs / 1e9:.0f} GPa, σ_y={yield_s / 1e6:.0f} MPa, UTS={uts / 1e6:.0f} MPa")
    fig.update_layout(height=PLOT_HEIGHT_STANDARD)

    formula = (
        f"**Elastic Modulus:** E = {youngs / 1e9:.1f} GPa\n\n"
        f"**Yield Strength:** σ_y = {yield_s / 1e6:.1f} MPa (ε_y = {yield_s / youngs * 100:.2f}%)\n\n"
        f"**Ultimate Tensile:** σ_UTS = {uts / 1e6:.1f} MPa\n\n"
        f"**Ramberg-Osgood n:** {n:.2f}\n\n"
        f"**Elastic Region:** ε < ε_y | **Plastic Region:** ε_y ≤ ε < ε_uts | **Failure:** ε ≥ ε_uts"
    )
    return fig, formula


def truss_analysis(joints: list[tuple[float, float]],
                   elements: list[tuple[int, int, float]],  # (i, j, area)
                   loads: list[tuple[int, float, float]],   # (node, fx, fy)
                   supports: list[tuple[int, bool, bool]],  # (node, fix_x, fix_y)
                   youngs: float = 200e9):
    """Simple 2D truss solver using direct stiffness method (FEM)."""
    n_nodes = len(joints)
    n_dof = 2 * n_nodes
    k_global = np.zeros((n_dof, n_dof))
    f_vec = np.zeros(n_dof)

    for node, fx, fy in loads:
        f_vec[2 * node] = fx
        f_vec[2 * node + 1] = fy

    for i, j, area in elements:
        xi, yi = joints[i]
        xj, yj = joints[j]
        dx = xj - xi
        dy = yj - yi
        L = math.sqrt(dx * dx + dy * dy)
        if L < 1e-6:
            continue
        c = dx / L
        s = dy / L
        k_e = (youngs * area / L) * np.array([
            [c*c, c*s, -c*c, -c*s],
            [c*s, s*s, -c*s, -s*s],
            [-c*c, -c*s, c*c, c*s],
            [-c*s, -s*s, c*s, s*s],
        ])
        dofs = [2*i, 2*i+1, 2*j, 2*j+1]
        for a in range(4):
            for b in range(4):
                k_global[dofs[a], dofs[b]] += k_e[a, b]

    fixed_dofs = []
    for node, fix_x, fix_y in supports:
        if fix_x:
            fixed_dofs.append(2 * node)
        if fix_y:
            fixed_dofs.append(2 * node + 1)
    free_dofs = [d for d in range(n_dof) if d not in fixed_dofs]

    k_ff = k_global[np.ix_(free_dofs, free_dofs)]
    f_f = f_vec[free_dofs]
    try:
        u_f = np.linalg.solve(k_ff, f_f)
    except np.linalg.LinAlgError:
        u_f = np.zeros_like(f_f)
    u = np.zeros(n_dof)
    u[free_dofs] = u_f

    reactions = k_global @ u
    forces = np.zeros(n_dof)
    forces[free_dofs] = f_f
    internal = np.zeros(len(elements))
    for idx, (i, j, area) in enumerate(elements):
        dx = joints[j][0] - joints[i][0]
        dy = joints[j][1] - joints[i][1]
        L = math.sqrt(dx*dx + dy*dy)
        if L < 1e-6:
            continue
        c = dx / L
        s = dy / L
        ui = u[2*i:2*i+2]
        uj = u[2*j:2*j+2]
        delta = np.array([c, s]) @ (uj - ui)
        internal[idx] = youngs * area * delta / L

    fig = go.Figure()
    for idx, (i, j, area) in enumerate(elements):
        xi, yi = joints[i]
        xj, yj = joints[j]
        uxi, uyi = u[2*i], u[2*i+1]
        uxj, uyj = u[2*j], u[2*j+1]
        scale = 100
        fig.add_trace(go.Scatter(
            x=[xi + uxi*scale, xj + uxj*scale],
            y=[yi + uyi*scale, yj + uyj*scale],
            mode="lines+text",
            line=dict(color="#3b82f6" if internal[idx] > 0 else "#ef4444", width=3),
            name=f"Element {idx} ({'T' if internal[idx] > 0 else 'C'}, {abs(internal[idx]) / 1000:.1f} kN)",
            text=[f"  {abs(internal[idx]) / 1000:.0f}kN"] if idx == 0 else [""],
            textposition="middle right",
        ))
    for node, fix_x, fix_y in supports:
        xi, yi = joints[node]
        uxi, uyi = u[2*node], u[2*node+1]
        fig.add_trace(go.Scatter(
            x=[xi + uxi*scale], y=[yi + uyi*scale],
            mode="markers", name=f"Support {node}",
            marker=dict(color="#22c55e", size=10, symbol="diamond"),
        ))
    fig.update_xaxes(title_text="X (m)")
    fig.update_yaxes(title_text="Y (m)", scaleanchor="x")
    fig = dark_layout(fig, f"2D Truss FEA — {len(elements)} elements, {n_nodes} nodes")
    fig.update_layout(height=PLOT_HEIGHT_STANDARD)

    max_f = max(abs(internal)) if len(internal) > 0 else 0
    info = (
        f"**Nodes:** {n_nodes} | **Elements:** {len(elements)}\n\n"
        f"**Max Internal Force:** {max_f / 1000:.1f} kN\n\n"
        f"**Max Deflection:** {max(np.abs(u)) * 1000:.2f} mm\n\n"
        f"**Positive = Tension (blue), Negative = Compression (red)**"
    )
    return fig, info


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
