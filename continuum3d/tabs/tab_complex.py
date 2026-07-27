"""Tab 5: Complex — Thermodynamics, Fluid Dynamics."""
import gradio as gr
from continuum3d.engines.thermodynamics import carnot_cycle, bernoulli_calc, ideal_gas_calc
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Thermodynamics, Systems & Fluid Dynamics")
    with gr.Row():
        with gr.Column(scale=6):
            c_plot = gr.Plot(label="Thermodynamic Analysis", show_label=False)
        with gr.Column(scale=4):
            c_mode = gr.Radio(["Carnot Cycle", "Bernoulli's Equation", "Ideal Gas Law"],
                              value="Carnot Cycle", label="System")

            with gr.Group() as c_carnot:
                c_th = gr.Slider(50, 1000, value=500, step=10, label="Hot Reservoir (\u00b0C)")
                c_tl = gr.Slider(-50, 200, value=50, step=5, label="Cold Reservoir (\u00b0C)")

            with gr.Group(visible=False) as c_bern:
                c_rho = gr.Slider(100, 2000, value=1000, step=10, label="Density (kg/m\u00b3)")
                c_bv = gr.Slider(0.1, 50, value=5, step=0.1, label="v\u2081 (m/s)")
                c_bh1 = gr.Slider(0, 100, value=10, step=0.5, label="h\u2081 (m)")
                c_bp = gr.Slider(0, 500000, value=101325, step=100, label="P\u2081 (Pa)")
                c_bh2 = gr.Slider(0, 100, value=2, step=0.5, label="h\u2082 (m)")

            with gr.Group(visible=False) as c_gas:
                c_gp = gr.Slider(1000, 1e7, value=101325, step=1000, label="Pressure (Pa)")
                c_gv = gr.Slider(0.001, 1, value=0.0224, step=0.001, label="Volume (m\u00b3)")
                c_gt = gr.Slider(-200, 2000, value=25, step=1, label="Temperature (\u00b0C)")

            c_btn = gr.Button("Calculate", variant="primary")
        with gr.Column(scale=6):
            c_formula = gr.Markdown(label="Thermodynamics", value="Select a system and calculate.")
            c_aibtn = gr.Button("\U0001f916 AI Thermodynamics Expert", size="sm")
            c_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Carnot Cycle"),
                gr.update(visible=mode == "Bernoulli's Equation"),
                gr.update(visible=mode == "Ideal Gas Law"))

    c_mode.change(_switch, [c_mode], [c_carnot, c_bern, c_gas])

    def _run(mode, th, tl, rho, bv, bh1, bp, bh2, gp, gv, gt):
        if mode == "Carnot Cycle":
            return carnot_cycle(th, tl)
        elif mode == "Bernoulli's Equation":
            return bernoulli_calc(rho, bv, bh1, bp, bh2)
        return ideal_gas_calc(gp, gv, gt)

    c_btn.click(_run,
                [c_mode, c_th, c_tl, c_rho, c_bv, c_bh1, c_bp, c_bh2, c_gp, c_gv, c_gt],
                [c_plot, c_formula])
    c_aibtn.click(
        lambda f: groq_query(f"Explain the thermodynamic principles: {f}",
                             "You are a thermodynamics professor."),
        [c_formula], [c_aiout],
    )
