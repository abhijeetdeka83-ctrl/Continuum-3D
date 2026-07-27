---
title: Continuum 3D
emoji: 🔧
colorFrom: blue
colorTo: slate
sdk: gradio
sdk_version: 5.12.0
app_file: app.py
pinned: true
license: mit
header: mini
---

<div align="center">

# Continuum 3D

**Open-source, zero-storage interactive 3D engineering workspace and generative CAD studio.**

Built with Gradio 5 · Plotly · trimesh · Groq Llama 3.3 70B · NumPy · SciPy

Runs free on [Hugging Face Spaces](https://huggingface.co/spaces) — zero infrastructure cost.

</div>

---

## What is this?

Continuum 3D is a browser-based engineering tool that combines **deterministic physics calculations** with **AI-powered generative design**. It runs entirely in a Gradio web interface, computes everything in real-time, and writes **nothing to permanent storage** — all 3D mesh files exist only in RAM via Python's `tempfile` module and are purged when the session ends.

You can run structural analysis, thermodynamic cycles, relativistic physics, generate parametric 3D models, and download watertight STL files for 3D printing — all from a single page.

## Features

| Category | What it does |
|----------|-------------|
| **7 Engineering Tabs** | General, Traditional, Advanced, Adaptive, Complex, Futuristic, Custom 3D Sandbox |
| **21 Physics Calculators** | Newton's laws, beam deflection, projectile motion, orbital mechanics, robot arm FK, stress-strain, hydraulic pressure, FEA heatmaps, Carnot cycle, Bernoulli, ideal gas, Schwarzschild radius, special relativity, wormhole embeddings |
| **8 Parametric 3D Shapes** | Cube, Sphere, Cylinder, Cone, Torus, Capsule, Pyramid, Gear — all with mesh repair |
| **3 Lattice Types** | Cubic, BCC, Octet — for lightweight structural design |
| **AI Text-to-3D** | Describe a shape in English → Groq generates parametric mesh |
| **Dual 3D-Print Pipeline** | Visual (prompt → mesh) and Precision (dimensions → OpenSCAD → STL) |
| **Dual Calculation Engine** | Deterministic (NumPy/SciPy, 0ms) + Dynamic AI (Groq LLM) |
| **Dark Slate UI** | Tailwind Slate-900 aesthetic, asymmetrical 60/25/15 layout |
| **Zero Storage** | All meshes use `tempfile` — auto-purged on session end |
| **STL/GLB Export** | Watertight mesh download with trimesh repair |

## Architecture

```
app.py                          → 16-line entry point
continuum3d/
├── config.py                   → GROQ_MODEL, GROQ_API_KEY, CSS, HEADER_HTML
├── ui/
│   └── layout.py               → build_theme() + build_app() — Gradio Blocks assembler
├── utils/
│   ├── plotly_utils.py         → dark_layout() — consistent dark theme for all figures
│   ├── groq_client.py          → Groq API client with 6 error handlers
│   ├── mesh_utils.py           → Ephemeral STL/GLB files, strut creation, mesh repair
│   └── units.py                → Unit conversion (6 categories) + dropdown sync
├── engines/
│   ├── physics.py              → 7 calculators (Newton, energy, projectile, orbital, robot arm, stress, hydraulic)
│   ├── beam.py                 → 3 beam types (Simply Supported, Cantilever, Fixed-Fixed)
│   ├── fea.py                  → FEA stress heatmap (4 load types)
│   ├── thermodynamics.py       → Carnot, Bernoulli, ideal gas
│   └── futuristic.py           → Schwarzschild, special relativity, wormholes
├── mesh/
│   ├── shapes.py               → 8 parametric shapes via trimesh + shapely
│   ├── lattice.py              → Cubic/BCC/Octet lattice generation
│   └── blueprint.py            → AI text-to-3D via Groq → parametric mesh
└── tabs/
    ├── tab_general.py          → Tab 1: Unit conversion + Newton's law + Energy
    ├── tab_traditional.py      → Tab 2: Beams + Stress-strain + Hydraulics
    ├── tab_advanced.py         → Tab 3: Projectile + Orbital + Robot arm
    ├── tab_adaptive.py         → Tab 4: Lattices + FEA heatmaps
    ├── tab_complex.py          → Tab 5: Carnot + Bernoulli + Ideal gas
    ├── tab_futuristic.py       → Tab 6: Black holes + Relativity + Wormholes
    └── tab_sandbox.py          → Tab 7: Parametric shapes + Text-to-3D + STL export
```

**Dependency flow** — zero import cycles:

```
app.py → ui/layout.py → tabs/* → engines/*, mesh/*, utils/*
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Gradio 5 | Web UI with reactive components |
| 3D Rendering | Plotly + WebGL | Real-time 3D viewport, heatmaps, subplots |
| Mesh Generation | trimesh + shapely | Parametric shapes, lattice structures, mesh repair |
| AI Engine | Groq API (Llama 3.3 70B) | Text-to-3D, engineering Q&A |
| Math | NumPy, SciPy, math | Deterministic calculations, interpolation |
| Hosting | Hugging Face Spaces | Free GPU inference via ZeroGPU |
| Export | STL, GLB | 3D printing and CAD import |

## Setup

### Option 1: Hugging Face Spaces (Recommended)

1. Fork or duplicate this Space on Hugging Face
2. Add `GROQ_API_KEY` as a Space secret (Settings → Variables and secrets → Secrets)
   - Get a free key at [console.groq.com](https://console.groq.com)
3. The app deploys automatically — all calculations work without the API key (AI features will be disabled)

### Option 2: Local

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/continuum-3d
cd continuum-3d
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"  # optional
python app.py
```

Open `http://localhost:7860` in your browser.

## Tab Reference

### Tab 1 — General
Unit conversion across 6 categories (Length, Mass, Temperature, Force, Energy, Pressure) with live formula display. Newton's Second Law and Energy Calculator with AI-powered deep-dive explanations.

### Tab 2 — Traditional
Beam deflection for Simply Supported, Cantilever, and Fixed-Fixed beams with bending moment diagrams. Stress-strain calculator with Young's modulus. Hydraulic pressure engine.

### Tab 3 — Advanced
Projectile motion with air drag visualization. Orbital mechanics (circular and elliptical orbits). Robot arm forward kinematics with 3D visualization.

### Tab 4 — Adaptive
Lattice structure generator (Cubic, BCC, Octet) with 3D viewport and STL download. FEA-style stress heatmap on rectangular plates (Point, Distributed, Cantilever Tip, Torsion loads).

### Tab 5 — Complex
Full Carnot cycle PV diagram with efficiency, work, and heat calculations. Bernoulli's equation with velocity/pressure profiles. Ideal gas law with multi-temperature PV isotherms.

### Tab 6 — Futuristic
Schwarzschild radius, Hawking temperature, and gravitational time dilation. Special relativity (Lorentz factor, length contraction). Morris-Thorne traversable wormhole embedding diagram.

### Tab 7 — Custom 3D Sandbox
8 parametric shapes with adjustable dimensions. AI text-to-3D generation via Groq. 3D viewport with GLB preview and STL/GLB download for 3D printing.

## Project Structure

```
continuum-3d/
├── app.py                      # Entry point (16 lines)
├── requirements.txt            # 7 dependencies
├── README.md                   # This file
└── continuum3d/                # Main package
    ├── config.py               # Constants and environment
    ├── ui/                     # Gradio theme and layout
    ├── utils/                  # Shared helpers
    ├── engines/                # Deterministic math
    ├── mesh/                   # 3D mesh generation
    └── tabs/                   # UI tab modules
```

**28 source files · 52 functions · 0 import cycles · 0 external storage**

## License

MIT — see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome. The codebase is modular — each tab, engine, and mesh generator is an isolated module. Add a new calculator by:

1. Creating a function in the appropriate `engines/` module
2. Adding a tab in `tabs/` that calls it
3. Registering the tab in `ui/layout.py`

## Acknowledgments

- [Groq](https://groq.com) for free LLM inference
- [Hugging Face](https://huggingface.co) for free GPU hosting
- [Gradio](https://gradio.app) for the web framework
- [trimesh](https://trimesh.org) for mesh processing
- [Plotly](https://plotly.com) for 3D visualization
