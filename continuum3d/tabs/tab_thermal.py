"""Tab: Thermal & Electrical — Heat transfer, DC/AC circuits."""
import gradio as gr
from continuum3d.engines.thermal import heat_conduction, heat_convection, heat_radiation
from continuum3d.engines.electrical import dc_circuit, rlc_circuit
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Heat Transfer & Electrical Engineering")
    with gr.Row():
        with gr.Column(scale=6):
            he_plot = gr.Plot(label="Analysis", show_label=False)
        with gr.Column(scale=4):
            he_mode = gr.Radio(
                ["Heat Conduction", "Heat Convection", "Heat Radiation",
                 "DC Circuit", "RLC Circuit"],
                value="Heat Conduction", label="Mode")

            with gr.Group() as he_cond:
                he_cl = gr.Slider(0.001, 5, value=0.5, step=0.01, label="Length (m)")
                he_ca = gr.Slider(0.0001, 1, value=0.01, step=0.001, label="Area (m\u00b2)")
                he_ck = gr.Slider(10, 500, value=200, step=1, label="Thermal k (W/m\u00b7K)")
                he_cth = gr.Slider(50, 1000, value=200, step=5, label="Hot Temp (\u00b0C)")
                he_ctc = gr.Slider(-50, 200, value=25, step=5, label="Cold Temp (\u00b0C)")

            with gr.Group(visible=False) as he_conv:
                he_ch = gr.Slider(1, 500, value=50, step=1, label="h (W/m\u00b2\u00b7K)")
                he_cva = gr.Slider(0.001, 10, value=0.5, step=0.01, label="Area (m\u00b2)")
                he_cts = gr.Slider(30, 500, value=150, step=5, label="Surface Temp (\u00b0C)")
                he_cta = gr.Slider(-20, 100, value=25, step=1, label="Ambient Temp (\u00b0C)")

            with gr.Group(visible=False) as he_rad:
                he_re = gr.Slider(0.01, 1, value=0.9, step=0.01, label="Emissivity \u03b5")
                he_ra = gr.Slider(0.001, 10, value=0.5, step=0.01, label="Area (m\u00b2)")
                he_rts = gr.Slider(50, 1500, value=500, step=10, label="Surface Temp (\u00b0C)")
                he_rta = gr.Slider(-50, 200, value=25, step=5, label="Surround Temp (\u00b0C)")

            with gr.Group(visible=False) as he_dc:
                he_dv = gr.Slider(1, 100, value=12, step=1, label="V_s (V)")
                he_dr1 = gr.Slider(1, 100000, value=100, step=10, label="R1 (\u03a9)")
                he_dr2 = gr.Slider(1, 100000, value=200, step=10, label="R2 (\u03a9)")
                he_dr3 = gr.Slider(1, 100000, value=300, step=10, label="R3 (\u03a9)")

            with gr.Group(visible=False) as he_rlc:
                he_rr = gr.Slider(1, 10000, value=100, step=1, label="R (\u03a9)")
                he_rl = gr.Slider(0.0001, 10, value=0.1, step=0.001, label="L (H)")
                he_rc = gr.Slider(1e-9, 1e-3, value=1e-6, step=1e-9, label="C (F)")
                he_rv = gr.Slider(1, 500, value=230, step=1, label="V_AC (V)")
                he_rf0 = gr.Slider(1, 1000, value=10, step=1, label="Freq Start (Hz)")
                he_rf1 = gr.Slider(1000, 1e6, value=100000, step=100, label="Freq End (Hz)")

            he_btn = gr.Button("Calculate", variant="primary")
        with gr.Column(scale=6):
            he_formula = gr.Markdown(label="Results", value="Select a mode and calculate.")
            he_aibtn = gr.Button("\U0001f916 AI Engineering Insight", size="sm")
            he_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Heat Conduction"),
                gr.update(visible=mode == "Heat Convection"),
                gr.update(visible=mode == "Heat Radiation"),
                gr.update(visible=mode == "DC Circuit"),
                gr.update(visible=mode == "RLC Circuit"))

    he_mode.change(_switch, [he_mode],
                   [he_cond, he_conv, he_rad, he_dc, he_rlc])

    def _run(mode, cl, ca, ck, cth, ctc,
             ch, cva, cts, cta,
             re, ra, rts, rta,
             dv, dr1, dr2, dr3,
             rr, rl, rc, rv, rf0, rf1):
        if mode == "Heat Conduction":
            return heat_conduction(cl, ca, ck, cth, ctc)
        elif mode == "Heat Convection":
            return heat_convection(ch, cva, cts, cta)
        elif mode == "Heat Radiation":
            return heat_radiation(re, ra, rts, rta)
        elif mode == "DC Circuit":
            return dc_circuit(dv, dr1, dr2, dr3)
        return rlc_circuit(rr, rl, rc, rv, rf0, rf1)

    he_inputs = [he_mode,
                 he_cl, he_ca, he_ck, he_cth, he_ctc,
                 he_ch, he_cva, he_cts, he_cta,
                 he_re, he_ra, he_rts, he_rta,
                 he_dv, he_dr1, he_dr2, he_dr3,
                 he_rr, he_rl, he_rc, he_rv, he_rf0, he_rf1]

    he_btn.click(_run, he_inputs, [he_plot, he_formula])
    for w in he_inputs:
        w.change(_run, he_inputs, [he_plot, he_formula])

    he_aibtn.click(
        lambda f: groq_query(f"Explain this thermal/electrical analysis: {f}",
                             "You are an expert engineer."),
        [he_formula], [he_aiout],
    )
