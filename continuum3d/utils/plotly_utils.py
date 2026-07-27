"""Plotly figure helpers — dark theme, layout defaults."""
import plotly.graph_objects as go


def dark_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent dark theme to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(color="#e2e8f0", size=16)),
        paper_bgcolor="#1e293b",
        plot_bgcolor="#0f172a",
        font=dict(color="#94a3b8"),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#475569"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#475569"),
        margin=dict(l=50, r=30, t=50, b=50),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    )
    return fig
