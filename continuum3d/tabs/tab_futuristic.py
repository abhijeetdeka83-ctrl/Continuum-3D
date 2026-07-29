"""Tab 6: Futuristic — Space Mechanics, Quantum & Speculative Physics."""
import gradio as gr
from continuum3d.engines.futuristic import schwarzschild_calc, relativistic_calc, wormhole_calc
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Space Mechanics, Quantum & Speculative Physics")
    with gr.Row():
        with gr.Column(scale=6):
            f_plot = gr.Plot(label="Visualization", show_label=False)
        with gr.Column(scale=4):
            f_mode = gr.Radio(["Black Hole (Schwarzschild)", "Special Relativity", "Wormhole"],
                              value="Black Hole (Schwarzschild)", label="Mode")

            with gr.Group() as f_bh:
                f_bhm = gr.Slider(0.1, 1e10, value=1.0, step=0.1, label="Mass (Solar Masses)")

            with gr.Group(visible=False) as f_rel:
                f_rv = gr.Slider(0.001, 0.999, value=0.5, step=0.001, label="v/c")
                f_rm = gr.Slider(0.01, 1000, value=1.0, step=0.01, label="Rest Mass (kg)")

            with gr.Group(visible=False) as f_wh:
                f_wr = gr.Slider(1, 1000, value=10, step=1, label="Throat Radius (m)")
                f_wt = gr.Slider(0, 100, value=1.0, step=0.1, label="Tidal Force (m/s\u00b2)")

            f_btn = gr.Button("Compute", variant="primary")
        with gr.Column(scale=6):
            f_formula = gr.Markdown(label="Relativistic Analysis", value="Select a model and compute.")
            f_aibtn = gr.Button("\U0001f916 AI Physics Deep-Dive", size="sm")
            f_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Black Hole (Schwarzschild)"),
                gr.update(visible=mode == "Special Relativity"),
                gr.update(visible=mode == "Wormhole"))

    f_mode.change(_switch, [f_mode], [f_bh, f_rel, f_wh])

    def _run(mode, bhm, rv, rm, wr, wt):
        if mode == "Black Hole (Schwarzschild)":
            return schwarzschild_calc(bhm)
        elif mode == "Special Relativity":
            return relativistic_calc(rv, rm)
        return wormhole_calc(wr, wt)

    f_btn.click(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_mode.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_bhm.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_rv.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_rm.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_wr.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_wt.change(_run, [f_mode, f_bhm, f_rv, f_rm, f_wr, f_wt], [f_plot, f_formula])
    f_aibtn.click(
        lambda f: groq_query(f"Deep physics explanation: {f}",
                             "You are a theoretical physicist."),
        [f_formula], [f_aiout],
    )
