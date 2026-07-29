"""Tab 2: Traditional — Beams, Stress/Strain, Hydraulics."""
import gradio as gr
from continuum3d.engines.beam import beam_deflection
from continuum3d.engines.physics import stress_strain_calc, hydraulic_pressure
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Mechanical Engineering \u2014 Beams, Stress/Strain, Hydraulics")
    with gr.Row():
        with gr.Column(scale=6):
            t_plot = gr.Plot(label="Engineering Analysis", show_label=False)
        with gr.Column(scale=4):
            t_mode = gr.Radio(["Beam Deflection", "Stress-Strain", "Hydraulic Pressure"],
                              value="Beam Deflection", label="Analysis Type")

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

            with gr.Group(visible=False) as t_hyd:
                t_hd = gr.Slider(0.1, 100, value=10, step=0.1, label="Depth (m)")
                t_hr = gr.Slider(500, 1500, value=1000, step=10, label="Density (kg/m\u00b3)")
                t_ha = gr.Slider(0.001, 1.0, value=0.01, step=0.001, label="Area (m\u00b2)")

            t_btn = gr.Button("Run Analysis", variant="primary")
        with gr.Column(scale=6):
            t_formula = gr.Markdown(label="Formulas", value="Select analysis type and run.")
            t_aibtn = gr.Button("\U0001f916 AI Engineering Insights", size="sm")
            t_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Beam Deflection"),
                gr.update(visible=mode == "Stress-Strain"),
                gr.update(visible=mode == "Hydraulic Pressure"))

    t_mode.change(_switch, [t_mode], [t_beam, t_stress, t_hyd])

    def _run(mode, btype, blen, bload, bei, bpos, sy, sa, sl, sf, hd, hr, ha):
        if mode == "Beam Deflection":
            return beam_deflection(btype, blen, bload, bei, bpos)
        elif mode == "Stress-Strain":
            return stress_strain_calc(sy, sa, sl, sf)
        return hydraulic_pressure(hd, hr, ha)

    t_btn.click(_run,
                [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                 t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_mode.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                         t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                  [t_plot, t_formula])
    t_btype.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                          t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                   [t_plot, t_formula])
    t_blen.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                         t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                  [t_plot, t_formula])
    t_bload.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                          t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                   [t_plot, t_formula])
    t_bei.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                        t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                 [t_plot, t_formula])
    t_bpos.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                         t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                  [t_plot, t_formula])
    t_sy.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_sa.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_sl.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_sf.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_hd.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_hr.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_ha.change(_run, [t_mode, t_btype, t_blen, t_bload, t_bei, t_bpos,
                       t_sy, t_sa, t_sl, t_sf, t_hd, t_hr, t_ha],
                [t_plot, t_formula])
    t_aibtn.click(
        lambda f: groq_query(f"Provide detailed engineering analysis: {f}",
                             "You are a senior mechanical engineer."),
        [t_formula], [t_aiout],
    )
