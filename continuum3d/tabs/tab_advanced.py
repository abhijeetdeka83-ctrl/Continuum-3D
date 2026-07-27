"""Tab 3: Advanced — Aerospace, Robotics, Kinematics."""
import gradio as gr
from continuum3d.engines.physics import projectile_motion, orbital_mechanics, robot_arm_fk
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Aerospace, Robotics & Kinematics")
    with gr.Row():
        with gr.Column(scale=6):
            a_plot = gr.Plot(label="Simulation", show_label=False)
        with gr.Column(scale=4):
            a_mode = gr.Radio(["Projectile Motion", "Orbital Mechanics", "Robot Arm FK"],
                              value="Projectile Motion", label="Mode")

            with gr.Group() as a_proj:
                a_v0 = gr.Slider(1, 200, value=50, step=1, label="Velocity (m/s)")
                a_ang = gr.Slider(5, 85, value=45, step=1, label="Angle (\u00b0)")
                a_g = gr.Slider(1, 25, value=9.81, step=0.1, label="Gravity (m/s\u00b2)")
                a_drag = gr.Slider(0, 0.5, value=0, step=0.01, label="Air Resistance")
                a_h0 = gr.Slider(0, 100, value=0, step=1, label="Initial Height (m)")

            with gr.Group(visible=False) as a_orb:
                a_om = gr.Slider(1e20, 2e30, value=5.972e24, step=1e23, label="Primary Mass (kg)")
                a_or = gr.Slider(1e5, 1e8, value=6.371e6, step=1e4, label="Body Radius (m)")
                a_oa = gr.Slider(0, 1e7, value=4e5, step=1e3, label="Altitude (m)")

            with gr.Group(visible=False) as a_robot:
                a_l1 = gr.Slider(0.1, 5, value=1.0, step=0.1, label="Link 1 (m)")
                a_l2 = gr.Slider(0.1, 5, value=0.8, step=0.1, label="Link 2 (m)")
                a_t1 = gr.Slider(-180, 180, value=45, step=5, label="\u03b8\u2081 (\u00b0)")
                a_t2 = gr.Slider(-180, 180, value=-30, step=5, label="\u03b8\u2082 (\u00b0)")

            a_btn = gr.Button("Simulate", variant="primary")
        with gr.Column(scale=6):
            a_formula = gr.Markdown(label="Analysis", value="Select mode and simulate.")
            a_aibtn = gr.Button("\U0001f916 AI Analysis", size="sm")
            a_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Projectile Motion"),
                gr.update(visible=mode == "Orbital Mechanics"),
                gr.update(visible=mode == "Robot Arm FK"))

    a_mode.change(_switch, [a_mode], [a_proj, a_orb, a_robot])

    def _run(mode, v0, ang, g, drag, h0, om, or_, oa, l1, l2, t1, t2):
        if mode == "Projectile Motion":
            return projectile_motion(v0, ang, g, drag, h0)
        elif mode == "Orbital Mechanics":
            return orbital_mechanics(om, or_, oa)
        return robot_arm_fk([l1, l2], [t1, t2])

    a_btn.click(_run,
                [a_mode, a_v0, a_ang, a_g, a_drag, a_h0, a_om, a_or, a_oa, a_l1, a_l2, a_t1, a_t2],
                [a_plot, a_formula])
    a_aibtn.click(
        lambda f: groq_query(f"Explain this aerospace/robotics analysis: {f}",
                             "You are an aerospace engineering professor."),
        [a_formula], [a_aiout],
    )
