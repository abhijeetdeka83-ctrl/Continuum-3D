"""Tab 7: Custom 3D Sandbox — Parametric, Text-to-3D, STL Export."""
import gradio as gr
from continuum3d.mesh.shapes import generate_shape
from continuum3d.mesh.blueprint import process_blueprint
from continuum3d.utils.groq_client import groq_query


def build_tab():
    gr.Markdown("### Text-to-3D | Parametric Shapes | Blueprint STL Generator")
    with gr.Row():
        with gr.Column(scale=6):
            s_3d = gr.Model3D(label="3D Viewport", height=520)
            s_file = gr.File(label="Download STL")
        with gr.Column(scale=4):
            s_mode = gr.Radio(["Parametric Shape", "Text to 3D", "Image to 3D"],
                              value="Parametric Shape", label="Mode")

            with gr.Group() as s_param:
                s_shape = gr.Dropdown(
                    ["Cube", "Sphere", "Cylinder", "Cone", "Torus", "Capsule", "Pyramid", "Gear"],
                    value="Cube", label="Shape")
                s_sx = gr.Slider(0.5, 20, value=5, step=0.5, label="Size X / Radius")
                s_sy = gr.Slider(0.5, 20, value=5, step=0.5, label="Size Y")
                s_sz = gr.Slider(0.5, 20, value=5, step=0.5, label="Size Z / Height")
                s_sub = gr.Slider(8, 64, value=16, step=4, label="Subdivisions")

            with gr.Group(visible=False) as s_text:
                s_prompt = gr.Textbox(
                    label="Describe your 3D object",
                    placeholder="e.g., A cylindrical vase, 10cm radius, 30cm tall",
                    lines=3,
                )

            with gr.Group(visible=False) as s_img:
                s_image = gr.Image(label="Reference Image", type="filepath")

            s_btn = gr.Button("Generate 3D Model", variant="primary", size="lg")
            s_info = gr.Markdown(label="Model Info", value="Choose a shape and click Generate.")
            s_aibtn = gr.Button("\U0001f916 AI 3D Design Assistant", size="sm")
            s_aiout = gr.Markdown()

    def _switch(mode):
        return (gr.update(visible=mode == "Parametric Shape"),
                gr.update(visible=mode == "Text to 3D"),
                gr.update(visible=mode == "Image to 3D"))

    s_mode.change(_switch, [s_mode], [s_param, s_text, s_img])

    def _run(mode, shape, sx, sy, sz, sub, prompt, image):
        if mode == "Parametric Shape":
            return generate_shape(shape, sx, sy, sz, int(sub))
        return process_blueprint(prompt, image, mode)

    s_btn.click(_run,
                [s_mode, s_shape, s_sx, s_sy, s_sz, s_sub, s_prompt, s_image],
                [s_3d, s_file, s_info])
    s_aibtn.click(
        lambda info: groq_query(
            f"Suggest improvements or variations for this 3D model: {info}",
            "You are a 3D modeling and CAD expert."),
        [s_info], [s_aiout],
    )
