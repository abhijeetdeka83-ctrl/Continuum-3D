"""Control systems — Transfer functions, PID, Bode plots, step response."""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from continuum3d.utils.plotly_utils import dark_layout
from continuum3d.config import PLOT_HEIGHT_MEDIUM


def pid_controller(kp: float, ki: float, kd: float, setpoint: float,
                   t_sim: float = 5, dt: float = 0.001):
    """PID controller simulation — step response with P, I, D components."""
    t = np.arange(0, t_sim, dt)
    n = len(t)
    err = np.zeros(n)
    p_out = np.zeros(n)
    i_out = np.zeros(n)
    d_out = np.zeros(n)
    output = np.zeros(n)
    integral = 0
    prev_err = setpoint

    for i in range(n):
        error = setpoint - output[i - 1] if i > 0 else setpoint
        err[i] = error
        integral += error * dt
        derivative = (error - prev_err) / dt if i > 0 else 0
        p_out[i] = kp * error
        i_out[i] = ki * integral
        d_out[i] = kd * derivative
        output[i] = p_out[i] + i_out[i] + d_out[i]
        prev_err = error

    output = output / max(abs(output)) * setpoint if max(abs(output)) > 0 else output

    fig = make_subplots(rows=2, cols=1, subplot_titles=("Step Response", "Control Components"))
    fig.add_trace(go.Scatter(x=t, y=output, mode="lines", name="Output",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0, t_sim], y=[setpoint, setpoint], mode="lines",
                             name=f"Setpoint ({setpoint})",
                             line=dict(color="#ef4444", width=2, dash="dash")), row=1, col=1)
    rise_time = t[np.argmin(np.abs(output - 0.9 * setpoint))] if setpoint > 0 else 0
    overshoot = max(0, (max(output) - setpoint) / setpoint * 100) if setpoint > 0 else 0
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_yaxes(title_text="Output", row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=p_out, mode="lines", name="P Term",
                             line=dict(color="#22c55e", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=i_out, mode="lines", name="I Term",
                             line=dict(color="#f59e0b", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=d_out, mode="lines", name="D Term",
                             line=dict(color="#a855f7", width=2)), row=2, col=1)
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Component Amplitude", row=2, col=1)
    fig = dark_layout(fig, f"PID Controller — Kp={kp}, Ki={ki}, Kd={kd}")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**PID Tuning:** K_p = {kp:.2f}, K_i = {ki:.2f}, K_d = {kd:.4f}\n\n"
        f"**Step Response:** Rise Time = {rise_time:.3f}s | Overshoot = {overshoot:.1f}%\n\n"
        f"**Steady State:** {output[-1]:.2f} (setpoint = {setpoint})"
    )
    return fig, formula


def transfer_function(num_coeffs: str, den_coeffs: str, f_start: float, f_end: float):
    """Transfer function Bode plot from polynomial coefficients."""
    try:
        num = [float(x) for x in num_coeffs.split(",")]
        den = [float(x) for x in den_coeffs.split(",")]
    except ValueError:
        fig = go.Figure()
        fig = dark_layout(fig, "Transfer Function — Invalid coefficients")
        return fig, "**Error:** Enter coefficients as comma-separated numbers (e.g., 1, 0, 100)"

    w = np.logspace(math.log10(f_start * 2 * math.pi), math.log10(f_end * 2 * math.pi), 500)
    s = 1j * w

    def poly_val(coeffs, s_val):
        return sum(c * s_val ** (len(coeffs) - 1 - i) for i, c in enumerate(coeffs))

    h = np.array([poly_val(num, si) / poly_val(den, si) if abs(poly_val(den, si)) > 1e-15 else 0
                  for si in s])
    mag_db = 20 * np.log10(np.abs(h) + 1e-15)
    phase_deg = np.degrees(np.angle(h))
    f_hz = w / (2 * math.pi)

    fig = make_subplots(rows=2, cols=1, subplot_titles=("Bode Magnitude", "Bode Phase"))
    fig.add_trace(go.Scatter(x=f_hz, y=mag_db, mode="lines", name="|H|",
                             line=dict(color="#3b82f6", width=3)), row=1, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
    fig.add_trace(go.Scatter(x=f_hz, y=phase_deg, mode="lines", name="∠H",
                             line=dict(color="#22c55e", width=3)), row=2, col=1)
    fig.add_hline(y=0, line=dict(color="#475569", width=1), row=2, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", type="log", row=2, col=1)
    fig.update_yaxes(title_text="Phase (°)", row=2, col=1)
    fig = dark_layout(fig, "Transfer Function Bode Plot")
    fig.update_layout(height=PLOT_HEIGHT_MEDIUM)

    formula = (
        f"**Numerator:** {num_coeffs}\n\n**Denominator:** {den_coeffs}\n\n"
        f"**DC Gain:** {mag_db[0]:.1f} dB\n\n"
        f"**At f={f_end:.0f} Hz:** {mag_db[-1]:.1f} dB, {phase_deg[-1]:.1f}°"
    )
    return fig, formula
