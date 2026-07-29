"""Tab 1: General — Physics Foundations & Unit Conversion."""
import gradio as gr
from continuum3d.utils.units import UNIT_TABLES, unit_convert, update_unit_dropdowns
from continuum3d.engines.physics import newtons_second_law, energy_calculator
from continuum3d.utils.groq_client import groq_query


def build_tab():
    """Build the General tab. Returns nothing — Gradio context manager handles registration."""
    gr.Markdown("### Physics Foundations & Unit Conversion")
    with gr.Row():
        with gr.Column(scale=6):
            g_plot = gr.Plot(label="Visualization", show_label=False)
        with gr.Column(scale=4):
            gr.Markdown("#### Unit Converter")
            g_ucat = gr.Dropdown(list(UNIT_TABLES.keys()), value="Length", label="Category")
            with gr.Row():
                g_ufrom = gr.Dropdown(list(UNIT_TABLES["Length"].keys()), value="m", label="From")
                g_uto = gr.Dropdown(list(UNIT_TABLES["Length"].keys()), value="ft", label="To")
            g_uval = gr.Number(value=1.0, label="Value")
            g_ures = gr.Textbox(label="Result", interactive=False)
            g_ubtn = gr.Button("Convert", variant="primary", size="sm")

            gr.Markdown("---")
            gr.Markdown("#### Physics Calculator")
            g_pmode = gr.Radio(["Newton's 2nd Law", "Energy Calculator"],
                               value="Newton's 2nd Law", label="Mode")
            g_mass = gr.Number(value=10, label="Mass (kg)")
            g_accel = gr.Number(value=9.81, label="Acceleration (m/s\u00b2)")
            g_height = gr.Number(value=5, label="Height (m)")
            g_vel = gr.Number(value=10, label="Velocity (m/s)")
            g_pbtn = gr.Button("Calculate", variant="primary")
        with gr.Column(scale=6):
            g_formula = gr.Markdown(label="Formulas", value="Select parameters and click Calculate.")
            g_aibtn = gr.Button("\U0001f916 AI Deep-Dive Explanation", size="sm")
            g_aiout = gr.Markdown()

    # Wire events
    g_ucat.change(update_unit_dropdowns, [g_ucat], [g_ufrom, g_uto])
    g_ubtn.click(unit_convert, [g_ucat, g_ufrom, g_uto, g_uval], [g_ures, g_formula])

    def _run(mode, m, a, h, v):
        if mode == "Newton's 2nd Law":
            return newtons_second_law(m, a)
        return energy_calculator(m, h, v)

    g_pbtn.click(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_pmode.change(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_mass.change(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_accel.change(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_height.change(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_vel.change(_run, [g_pmode, g_mass, g_accel, g_height, g_vel], [g_plot, g_formula])
    g_aibtn.click(
        lambda f: groq_query(f"Explain this physics in detail: {f}",
                             "You are a physics professor. Be clear and thorough."),
        [g_formula], [g_aiout],
    )
