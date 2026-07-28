"""FEA heatmap engine — deterministic stress distribution visualization."""
import math
import numpy as np
import plotly.graph_objects as go
from continuum3d.utils.plotly_utils import dark_layout


def fea_heatmap(stress_type: str, max_stress: float, num_elements: int):
    """Deterministic FEA-style stress heatmap on a rectangular plate."""
    n = max(int(math.sqrt(num_elements)), 4)
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x, y)

    if stress_type == "Point Load (Center)":
        Z = max_stress / ((X - 0.5) ** 2 + (Y - 0.5) ** 2 + 0.01)
    elif stress_type == "Distributed Load":
        Z = max_stress * X * (1 - X) * 4
    elif stress_type == "Cantilever Tip":
        Z = max_stress * X * (1 + 3 * (1 - X))
    else:
        Z = max_stress * np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2) * 2

    Z = np.clip(Z, 0, max_stress * 1.2)
    fig = go.Figure(data=go.Heatmap(
        z=Z, x=x, y=y, colorscale="Viridis",
        colorbar=dict(title="Stress (Pa)", titlefont=dict(color="#94a3b8"),
                      tickfont=dict(color="#94a3b8")),
    ))
    fig.update_xaxes(title_text="X (normalized)")
    fig.update_yaxes(title_text="Y (normalized)")
    fig = dark_layout(fig, f"FEA Stress \u2014 {stress_type}")
    fig.update_layout(height=450)

    peak, avg = np.max(Z), np.mean(Z)
    formula = (
        f"**Peak Stress:** {peak:.2f} Pa ({peak / max_stress * 100:.1f}% of input max)\n\n"
        f"**Average Stress:** {avg:.2f} Pa\n\n"
        f"**Stress Concentration Factor:** {peak / avg:.2f}\n\n"
        f"**Elements:** {n}\u00d7{n} = {n * n}\n\n"
        f"*Deterministic mesh \u2014 zero AI cost*"
    )
    return fig, formula
