"""Report export utilities — HTML reports with embedded plots."""
import tempfile
from typing import Optional

import plotly.graph_objects as go


def export_plot_to_html(fig: go.Figure, formula_md: str) -> Optional[str]:
    """Export a Plotly figure + formula to a standalone HTML file."""
    try:
        html = fig.to_html(full_html=True, include_plotlyjs="cdn")
        report = (
            "<html><head><meta charset='utf-8'>"
            "<style>"
            "body{font-family:sans-serif;background:#0f172a;color:#e2e8f0;padding:20px}"
            "h1{color:#3b82f6}"
            ".formula{background:#1e293b;padding:15px;border-radius:8px;margin:10px 0}"
            "</style></head><body>"
            "<h1>Continuum 3D — Analysis Report</h1>"
            f"<div class='formula'>{formula_md}</div>"
            f"{html}</body></html>"
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, dir=tempfile.gettempdir())
        tmp.write(report.encode("utf-8"))
        tmp.close()
        return tmp.name
    except Exception:
        return None
