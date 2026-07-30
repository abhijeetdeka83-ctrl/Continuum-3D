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

Built with Gradio 5 · Plotly · trimesh · Groq Llama 3.3 70B · NumPy

Runs free on [Hugging Face Spaces](https://huggingface.co/spaces) — zero infrastructure cost.

</div>

---

## What is this?

Continuum 3D is a browser-based engineering tool combining **deterministic physics calculations** with **AI-powered generative design** and **parametric CAD**. It runs entirely in Gradio, computes in real-time, and writes **nothing to permanent storage** — all 3D meshes exist only in RAM via `tempfile`, purged when the session ends.

## Features

| Category | What it does |
|----------|-------------|
| **9 Engineering Tabs** | General, Traditional, Advanced, Adaptive, Complex, Futuristic, Thermal/Electrical, Custom 3D Sandbox, Assembly |
| **25+ Physics Calculators** | Newton's laws, beam deflection, stress-strain, hydraulic pressure, projectile motion, orbital mechanics, robot FK, FEA heatmaps, buckling, torsion, vibration, fatigue, Carnot cycle, Bernoulli, ideal gas, heat transfer (conduction/convection/radiation), DC/RLC circuits, PID control, transfer functions, pipe flow, Moody chart, Schwarzschild radius, special relativity, wormholes |
| **CAD Operations** | Shell/Hollow, Linear/Circular Pattern, Revolve, Loft, Import Mesh, Boolean (Union/Subtract/Intersect) |
| **Multi-Body Assembly** | Add/remove bodies, position/rotation transforms, editable Dataframe body list |
| **8 Parametric 3D Shapes** | Cube, Sphere, Cylinder, Cone, Torus, Capsule, Pyramid, Gear |
| **3 Lattice Types** | Cubic, BCC, Octet for lightweight structural design |
| **AI Text-to-3D** | Describe a shape → Groq generates parametric mesh |
| **Undo/Redo** | 50-step mesh history with session save/load |
| **Multi-Format Export** | STL, OBJ, PLY, 3MF, GLB, COLLADA DAE, OFF + HTML report export |
| **Dual Calculation Engine** | Deterministic (NumPy, 0ms latency) + Dynamic AI (Groq Llama 3.3 70B) |
| **Dark Slate UI** | Tailwind Slate-900 aesthetic, configurable theme hues |
| **Zero Storage** | All files use `tempfile` — auto-purged on session end |

## Architecture

```
app.py                                              — 18-line entry point
continuum3d/
├── config.py                                       → 20+ constants, env vars, theme hues
├── ui/
│   └── layout.py                                   → build_theme() + build_app() — 9-tab assembler
├── utils/
│   ├── plotly_utils.py                             → dark_layout() — consistent dark Plotly theme
│   ├── groq_client.py                              → Groq API client with 6 error handlers
│   ├── mesh_utils.py                               → EXPORT_FORMATS dict, create_ephemeral_file()
│   ├── history.py                                  → MeshHistory (50-step undo/redo, JSON save/load)
│   ├── report_export.py                            → export_plot_to_html() — standalone engineering reports
│   └── units.py                                    → Unit conversion (6 categories) + dropdown sync
├── engines/
│   ├── physics.py                                  → Newton, Energy, Projectile, Orbital, Robot FK, Stress, Hydraulic
│   ├── beam.py                                     → 3 beam types: Simply Supported, Cantilever, Fixed-Fixed
│   ├── fea.py                                      → FEA stress heatmaps (4 load cases)
│   ├── structural.py                               → Column Buckling, Torsion, Beam Bending (SFD/BMD), Stress-Strain, 2D Truss FEA
│   ├── dynamics.py                                 → SDOF Vibration (FRF/impulse), Fatigue S-N (Miner's rule)
│   ├── thermodynamics.py                           → Carnot cycle, Bernoulli, Ideal Gas
│   ├── thermal.py                                  → Fourier Conduction, Newton Convection, Stefan-Boltzmann Radiation
│   ├── electrical.py                               → DC series/parallel, RLC Bode plots
│   ├── control.py                                  → PID Step Response, Transfer Function Bode
│   ├── fluids.py                                   → Darcy-Weisbach Pipe Flow, Moody Chart
│   ├── futuristic.py                               → Schwarzschild radius, Relativity, Wormholes
│   ├── cad_ops.py                                  → revolve_profile(), sweep_profile(), loft_profiles()
│   └── assembly.py                                 → Assembly/AssemblyBody with multi-body transforms
├── mesh/
│   ├── shapes.py                                   → 8 parametric shapes via trimesh + shapely
│   ├── lattice.py                                  → Cubic/BCC/Octet lattice generation
│   └── blueprint.py                                → AI text-to-3D via Groq → parametric mesh generation
└── tabs/
    ├── tab_general.py                              → Tab 1: Unit converter + Newton + Energy
    ├── tab_traditional.py                          → Tab 2: Beam Deflection + Stress-Strain + Buckling + Torsion + Hydraulics + SFD/BMD + Truss FEA
    ├── tab_advanced.py                             → Tab 3: Projectile + Orbital + Robot + Vibration + Fatigue
    ├── tab_adaptive.py                             → Tab 4: Lattices + FEA heatmaps
    ├── tab_complex.py                              → Tab 5: Carnot + Bernoulli + Gas + PID + Transfer Function + Pipe Flow + Moody
    ├── tab_futuristic.py                           → Tab 6: Black holes + Relativity + Wormholes
    ├── tab_thermal.py                              → Tab 7: Conduction + Convection + Radiation + DC + RLC
    ├── tab_sandbox.py                              → Tab 8: Parametric shapes + Text-to-3D + Boolean + Shell/Pattern + Revolve/Loft + Import + Undo/Redo + Save/Load
    └── tab_assembly.py                             → Tab 9: Multi-body assembly with transforms
```

## Quick Start

### Hugging Face (Recommended)

1. Fork on Hugging Face Spaces
2. Add `GROQ_API_KEY` as a Space secret
3. Auto-deploys — all deterministic calcs work without API key

### Local

```bash
git clone https://github.com/abhijeetdeka83-ctrl/Continuum-3D
cd Continuum-3D
pip install -r requirements.txt
set GROQ_API_KEY=your-key-here  # optional
python app.py
```

Open `http://localhost:7860`.

## Tab Reference

### Tab 1 — General
Unit conversion (Length/Mass/Temperature/Force/Energy/Pressure), Newton's Second Law, Energy Calculator with AI deep-dive.

### Tab 2 — Traditional
Beam deflection (3 support types), Stress-Strain (Ramberg-Osgood), Column Buckling (Euler/Johnson), Torsion, Hydraulics, Beam Bending (SFD/BMD), 2D Truss FEA.

### Tab 3 — Advanced
Projectile motion (with drag), Orbital mechanics, Robot arm FK, SDOF Vibration (FRF + impulse), Fatigue S-N (Miner's rule).

### Tab 4 — Adaptive
Lattice generator (Cubic/BCC/Octet), FEA stress heatmaps (4 load types).

### Tab 5 — Complex
Carnot cycle PV, Bernoulli, Ideal Gas, PID Step Response, Transfer Function Bode, Darcy-Weisbach Pipe Flow, Moody Chart.

### Tab 6 — Futuristic
Schwarzschild radius, Hawking temperature, time dilation, Special relativity (Lorentz, length contraction), Morris-Thorne wormholes.

### Tab 7 — Thermal & Electrical
Fourier conduction, Newton convection, Stefan-Boltzmann radiation, DC circuits, RLC Bode analysis.

### Tab 8 — Custom 3D Sandbox
8 parametric shapes, AI Text-to-3D, Boolean Ops (Union/Subtract/Intersect), Shell/Hollow, Linear Pattern, Import Mesh, Revolve, Loft. Undo/Redo (50-step), session Save/Load. Multi-format export.

### Tab 9 — Assembly
Multi-body composition with editable Dataframe, position/rotation transforms, GLB preview, STL/OBJ/PLY/3MF export.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Gradio 5 | Web UI with reactive .change() handlers |
| 3D Rendering | Plotly + WebGL + trimesh | Viewport, heatmaps, subplots |
| Mesh | trimesh + shapely + scad | Parametric shapes, booleans, repair |
| AI | Groq API (Llama 3.3 70B) | Text-to-3D, engineering Q&A |
| Math | NumPy, math | Deterministic calculations |
| Hosting | Hugging Face Spaces | Free deployment |
| Export | STL, OBJ, PLY, 3MF, GLB, DAE, OFF + HTML | 3DP, CAD, reporting |

## Stats

- **38 source files · 65+ functions · 0 import cycles · 0 external storage**
- 9 tabs · 25+ physics engines · 8 export formats · 50-step undo
- 8 parametric shapes · 3 lattice types · Boolean/CAD/Assembly ops

## Development Journey

This project went through several architectural pivots — from an ambitious all-in-one cross-domain engineering suite (3D CAD + PCB + FEA + math), through the harsh realities of zero-cost cloud infrastructure, to the final **stateless, ephemeral-storage design** that makes \$0 hosting possible.

The full technical retrospective — including the original vision, the storage crisis that forced a redesign, the tradeoffs made, current flaws, and what I'd do differently — is documented here:

➡️ **[docs/engineering-retrospective.mdx](docs/engineering-retrospective.mdx)**

## License

MIT — see [LICENSE](LICENSE).

## Contributing

One function per engine module, one tab module per UI tab, register in `ui/layout.py`. Follow the dependency flow: `tabs/ → engines/, mesh/, utils/`.
