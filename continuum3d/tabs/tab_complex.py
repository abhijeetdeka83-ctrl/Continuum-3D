"""Tab 5: Complex — Thermodynamics, Control Systems, Fluid Dynamics."""
import gradio as gr
from continuum3d.engines.thermodynamics import carnot_cycle, bernoulli_calc, ideal_gas_calc
from continuum3d.engines.control import pid_controller, transfer_function
from continuum3d.engines.fluids import pipe_flow, moody_chart
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Thermodynamics, Control Systems & Fluid Dynamics")
    with gr.Row():
        with gr.Column(scale=6):
            c_plot = gr.Plot(label="Analysis", show_label=False)
        with gr.Column(scale=4):
            c_mode = gr.Radio(
                ["Carnot Cycle", "Bernoulli's Equation", "Ideal Gas Law",
                 "PID Controller", "Transfer Function",
                 "Pipe Flow", "Moody Chart"],
                value="Carnot Cycle", label="System")

            with gr.Group() as c_carnot:
                c_th = gr.Slider(50, 1000, value=500, step=10, label="Hot Reservoir (\u00b0C)")
                c_tl = gr.Slider(-50, 200, value=50, step=5, label="Cold Reservoir (\u00b0C)")
                c_moles = gr.Slider(0.1, 10, value=1.0, step=0.1, label="Moles of Gas")
                c_ratio = gr.Slider(1.1, 5, value=1.8, step=0.1, label="Expansion Ratio")
                c_gamma = gr.Dropdown(
                    [("Monatomic (5/3=1.667)", 1.667),
                     ("Diatomic (7/5=1.4)", 1.4),
                     ("Polyatomic (9/7=1.286)", 1.286)],
                    value=1.4, label="Heat Capacity Ratio (\u03b3)")

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

            with gr.Group(visible=False) as c_pid:
                c_kp = gr.Slider(0.1, 50, value=5, step=0.1, label="Kp")
                c_ki = gr.Slider(0, 20, value=2, step=0.1, label="Ki")
                c_kd = gr.Slider(0, 5, value=0.1, step=0.01, label="Kd")
                c_sp = gr.Slider(0.1, 100, value=10, step=0.1, label="Setpoint")

            with gr.Group(visible=False) as c_tf:
                c_num = gr.Textbox(value="1, 0, 100", label="Numerator (comma-sep)")
                c_den = gr.Textbox(value="1, 10, 100", label="Denominator (comma-sep)")
                c_tf0 = gr.Slider(0.1, 10, value=0.1, step=0.1, label="Freq Start (Hz)")
                c_tf1 = gr.Slider(10, 10000, value=1000, step=10, label="Freq End (Hz)")

            with gr.Group(visible=False) as c_pipe:
                c_pq = gr.Slider(0.001, 1, value=0.05, step=0.001, label="Flow Rate (m\u00b3/s)")
                c_pd = gr.Slider(0.01, 1, value=0.1, step=0.01, label="Diameter (m)")
                c_pl = gr.Slider(1, 1000, value=100, step=1, label="Length (m)")
                c_prho = gr.Slider(100, 2000, value=1000, step=10, label="Density (kg/m\u00b3)")
                c_pmu = gr.Slider(1e-6, 1, value=0.001, step=0.0001, label="Viscosity (Pa\u00b7s)")
                c_pr = gr.Slider(0, 0.01, value=0.0001, step=0.00001, label="Roughness (m)")

            with gr.Group(visible=False) as c_moody:
                c_mre = gr.Slider(10, 1e7, value=50000, step=100, label="Reynolds Number")
                c_mer = gr.Slider(0, 0.05, value=0.001, step=0.0001, label="Rel. Roughness \u03b5/D")

            c_btn = gr.Button("Calculate", variant="primary")
        with gr.Column(scale=6):
            c_formula = gr.Markdown(label="Results", value="Select a system and calculate.")
            c_aibtn = gr.Button("\U0001f916 AI Expert Insight", size="sm")
            c_aiout = gr.Markdown()

    groups = [c_carnot, c_bern, c_gas, c_pid, c_tf, c_pipe, c_moody]

    def _switch(mode):
        return [gr.update(visible=(i == 0 and mode == "Carnot Cycle") or
                          (i == 1 and mode == "Bernoulli's Equation") or
                          (i == 2 and mode == "Ideal Gas Law") or
                          (i == 3 and mode == "PID Controller") or
                          (i == 4 and mode == "Transfer Function") or
                          (i == 5 and mode == "Pipe Flow") or
                          (i == 6 and mode == "Moody Chart"))
                for i in range(len(groups))]

    c_mode.change(_switch, [c_mode], groups)

    def _run(mode, th, tl, moles, ratio, gamma,
             rho, bv, bh1, bp, bh2, gp, gv, gt,
             kp, ki, kd, sp,
             num, den, tf0, tf1,
             pq, pd, pl, prho, pmu, pr,
             mre, mer):
        if mode == "Carnot Cycle":
            return carnot_cycle(th, tl, moles, ratio, gamma)
        elif mode == "Bernoulli's Equation":
            return bernoulli_calc(rho, bv, bh1, bp, bh2)
        elif mode == "Ideal Gas Law":
            return ideal_gas_calc(gp, gv, gt)
        elif mode == "PID Controller":
            return pid_controller(kp, ki, kd, sp)
        elif mode == "Transfer Function":
            return transfer_function(num, den, tf0, tf1)
        elif mode == "Pipe Flow":
            return pipe_flow(pq, pd, pl, prho, pmu, pr)
        return moody_chart(mre, mer)

    c_inputs = [c_mode,
                c_th, c_tl, c_moles, c_ratio, c_gamma,
                c_rho, c_bv, c_bh1, c_bp, c_bh2,
                c_gp, c_gv, c_gt,
                c_kp, c_ki, c_kd, c_sp,
                c_num, c_den, c_tf0, c_tf1,
                c_pq, c_pd, c_pl, c_prho, c_pmu, c_pr,
                c_mre, c_mer]

    c_btn.click(_run, c_inputs, [c_plot, c_formula])
    for w in c_inputs:
        w.change(_run, c_inputs, [c_plot, c_formula])

    c_aibtn.click(
        lambda f: groq_query(f"Explain the engineering principles: {f}",
                             "You are an expert engineer."),
        [c_formula], [c_aiout],
    )
