"""
Continuum 3D — Entry Point
Zero-Storage Interactive 3D Engineering Workspace & Generative CAD Studio

Architecture:
  continuum3d/
  ├── config.py        — Constants, env vars, CSS
  ├── utils/           — Shared helpers (plotly, groq, mesh, units)
  ├── engines/         — Deterministic math engines (physics, thermo, beam, fea, futuristic)
  ├── mesh/            — 3D mesh generation (shapes, lattice, blueprint)
  ├── tabs/            — Gradio tab modules (one per section)
  └── ui/              — Layout builder and theme
"""
from continuum3d.ui.layout import build_app

if __name__ == "__main__":
    demo = build_app()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
