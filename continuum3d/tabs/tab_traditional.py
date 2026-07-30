"""Tab 2: Traditional — Beams, Stress/Strain, Hydraulics, Buckling, Torsion."""
import gradio as gr
from continuum3d.engines.beam import beam_deflection
from continuum3d.engines.physics import stress_strain_calc, hydraulic_pressure
from continuum3d.engines.structural import column_buckling, torsion_shaft, beam_bending, stress_strain, truss_analysis
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Mechanical Engineering \u2014 Beams, Stress, Buckling, Torsion, FEA, Hydraulics")
    with gr.Row():
        with gr.Column(scale=6):
            t_plot = gr.Plot(label="Engineering Analysis", show_label=False)
        with gr.Column(scale=4):
            t_mode = gr.Radio([
                "Beam Deflection", "Stress-Strain", "Column Buckling",
                "Torsion", "Hydraulic Pressure",
                "Beam Bending (SFD/BMD)", "2D Truss FEA",
            ], value="Beam Deflection", label="Analysis Type")

            with gr.Group() as t_beam:
                t_btype = gr.Dropdown(["Simply Supported", "Cantilever", "Fixed-Fixed"],
                                       value="Simply Supported", label="Beam Type")
                t_blen = gr.Slider(0.5, 20, value=5, step=0.1, label="Length (m)")
                t_bload = gr.Slider(100, 10000, value=1000, step=50, label="Load (N)")
                t_bei = gr.Slider(1e3, 1e8, value=1e6, step=1e3, label="EI (N\u00b7m\u00b2)")
                t_bpos = gr.Slider(0.05, 0.95, value=0.5, step=0.05, label="Load Position")

            with gr.Group(visible=False) as t_stress:
                t_sy = gr.Slider(1e6, 1e12, value=200e9, step=1e9, label="Young's Modulus (Pa)")
                t_sa = gr.Slider(1e-5, 0.01, value=1e-3, step=1e-5, label="Cross-Section (m\u00b2)")
                t_sl = gr.Slider(0.1, 10, value=1.0, step=0.1, label="Length (m)")
                t_sf = gr.Slider(10, 1e6, value=50000, step=100, label="Force (N)")

            with gr.Group(visible=False) as t_buck:
                t_bk_end = gr.Dropdown(
                    ["Pinned-Pinned", "Fixed-Fixed", "Fixed-Free", "Fixed-Pinned"],
                    value="Pinned-Pinned", label="End Condition")
                t_bk_e = gr.Slider(1e6, 1e12, value=200e9, step=1e9, label="Young's Modulus (Pa)")
                t_bk_l = gr.Slider(0.2, 20, value=3.0, step=0.1, label="Column Length (m)")
                t_bk_i = gr.Slider(1e-10, 1e-2, value=1e-6, step=1e-7, label="Min Area Moment I (m\u2074)")
                t_bk_a = gr.Slider(1e-5, 0.01, value=1e-3, step=1e-5, label="Cross-Section Area (m\u00b2)")
                t_bk_y = gr.Slider(1e6, 1e10, value=250e6, step=1e6, label="Yield Strength (Pa)")

            with gr.Group(visible=False) as t_tor:
                t_tr = gr.Slider(0.005, 0.5, value=0.05, step=0.005, label="Shaft Radius (m)")
                t_tt = gr.Slider(10, 50000, value=1000, step=10, label="Torque (N\u00b7m)")
                t_tg = gr.Slider(1e9, 100e9, value=80e9, step=1e9, label="Shear Modulus (Pa)")
                t_tl = gr.Slider(0.1, 10, value=1.0, step=0.1, label="Shaft Length (m)")

            with gr.Group(visible=False) as t_hyd:
                t_hd = gr.Slider(0.1, 100, value=10, step=0.1, label="Depth (m)")
                t_hr = gr.Slider(500, 1500, value=1000, step=10, label="Density (kg/m\u00b3)")
                t_ha = gr.Slider(0.001, 1.0, value=0.01, step=0.001, label="Area (m\u00b2)")

            with gr.Group(visible=False) as t_beam2:
                t_b2_s = gr.Slider(1, 20, value=5, step=0.5, label="Span (m)")
                t_b2_p = gr.Slider(100, 50000, value=10000, step=100, label="Point Load (N)")
                t_b2_a = gr.Slider(0.1, 0.9, value=0.4, step=0.05, label="Load Position (frac)")
                t_b2_e = gr.Slider(1e9, 1e12, value=200e9, step=1e9, label="E (Pa)")
                t_b2_i = gr.Slider(1e-8, 1e-2, value=1e-5, step=1e-6, label="I (m\u2074)")

            with gr.Group(visible=False) as t_truss:
                gr.Markdown("**2D Truss FEA — 4-bar example**")
                t_tr_e = gr.Slider(50e9, 300e9, value=200e9, step=10e9, label="E (Pa)")
                t_tr_a = gr.Slider(1e-5, 0.01, value=1e-3, step=1e-4, label="Area (m\u00b2)")
                t_tr_fx = gr.Slider(-50000, 50000, value=0, step=100, label="Load Fx (N)")
                t_tr_fy = gr.Slider(-50000, 50000, value=-10000, step=100, label="Load Fy (N)")

            t_btn = gr.Button("Run Analysis", variant="primary")
        with gr.Column(scale=6):
            t_formula = gr.Markdown(label="Formulas", value="Select analysis type and run.")
            t_aibtn = gr.Button("\U0001f916 AI Engineering Insights", size="sm")
            t_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Beam Deflection"),
                gr.update(visible=mode == "Stress-Strain"),
                gr.update(visible=mode == "Column Buckling"),
                gr.update(visible=mode == "Torsion"),
                gr.update(visible=mode == "Hydraulic Pressure"),
                gr.update(visible=mode == "Beam Bending (SFD/BMD)"),
                gr.update(visible=mode == "2D Truss FEA"))

    t_mode.change(_switch, [t_mode],
                  [t_beam, t_stress, t_buck, t_tor, t_hyd, t_beam2, t_truss])

    def _run(mode, btype, blen, bload, bei, bpos,
             sy, sa, sl, sf,
             bk_end, bk_e, bk_l, bk_i, bk_a, bk_y,
             tr, tt, tg, tl,
             hd, hr, ha,
             b2_s, b2_p, b2_a, b2_e, b2_i,
             tr_e, tr_a, tr_fx, tr_fy):
        if mode == "Beam Deflection":
            return beam_deflection(btype, blen, bload, bei, bpos)
        elif mode == "Stress-Strain":
            stress_val = sf / sa if sa > 0 else 1e6
            return stress_strain(sy, stress_val * 0.5, stress_val)
        elif mode == "Column Buckling":
            return column_buckling(bk_end, bk_e, bk_l, bk_i, bk_a, bk_y)
        elif mode == "Torsion":
            return torsion_shaft(tr, tt, tg, tl)
        elif mode == "Hydraulic Pressure":
            return hydraulic_pressure(hd, hr, ha)
        elif mode == "Beam Bending (SFD/BMD)":
            return beam_bending(b2_s, b2_p, b2_a * b2_s, b2_e, b2_i)
        elif mode == "2D Truss FEA":
            joints = [(0, 0), (b2_s * 0.5, 0), (0.5, 0.5)]
            elements = [(0, 1, tr_a), (1, 2, tr_a), (0, 2, tr_a)]
            loads = [(1, tr_fx, tr_fy)]
            supports = [(0, True, True), (2, True, True)]
            return truss_analysis(joints, elements, loads, supports, tr_e)
        return gr.update(), ""

    t_inputs = [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                t_sy, t_sa, t_sl, t_sf,
                t_bk_end, t_bk_e, t_bk_l, t_bk_i, t_bk_a, t_bk_y,
                t_tr, t_tt, t_tg, t_tl,
                t_hd, t_hr, t_ha,
                t_b2_s, t_b2_p, t_b2_a, t_b2_e, t_b2_i,
                t_tr_e, t_tr_a, t_tr_fx, t_tr_fy]

    t_btn.click(_run, t_inputs, [t_plot, t_formula])
    for w in t_inputs:
        w.change(_run, t_inputs, [t_plot, t_formula])

    t_aibtn.click(
        lambda f: groq_query(f"Provide detailed engineering analysis: {f}",
                             "You are a senior mechanical engineer."),
        [t_formula], [t_aiout],
    )
