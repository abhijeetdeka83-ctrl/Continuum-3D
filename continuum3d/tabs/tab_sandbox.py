"""Tab 7: Custom 3D Sandbox — Parametric, Text-to-3D, Boolean Ops, Multi-Format Export."""
import gradio as gr
from continuum3d.mesh.shapes import generate_shape
from continuum3d.mesh.blueprint import process_blueprint
from continuum3d.utils.groq_client import groq_query
from continuum3d.utils.mesh_utils import EXPORT_FORMATS, create_ephemeral_file
import trimesh
import numpy as np


def _gen_shape(shape, sx, sy, sz, subdiv):
    if shape == "Cube":
        return trimesh.creation.box(extents=[sx, sy, sz])
    elif shape == "Sphere":
        return trimesh.creation.icosphere(subdivisions=max(subdiv, 2), radius=sx / 2)
    elif shape == "Cylinder":
        return trimesh.creation.cylinder(radius=sx / 2, height=sz, sections=max(subdiv * 4, 16))
    elif shape == "Cone":
        return trimesh.creation.cone(radius=sx / 2, height=sz, sections=max(subdiv * 4, 16))
    elif shape == "Torus":
        return trimesh.creation.torus(major_radius=sx / 2, minor_radius=sz / 2,
                                      major_segments=max(subdiv * 4, 16),
                                      minor_segments=max(subdiv * 2, 8))
    elif shape == "Capsule":
        return trimesh.creation.capsule(radius=sx / 2, height=sz,
                                        sections=max(subdiv * 2, 16),
                                        sections_cap=max(subdiv, 8))
    elif shape == "Pyramid":
        verts = np.array([
            [-sx / 2, -sy / 2, 0], [sx / 2, -sy / 2, 0],
            [sx / 2, sy / 2, 0], [-sx / 2, sy / 2, 0],
            [0, 0, sz],
        ])
        faces = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
        return trimesh.Trimesh(vertices=verts, faces=faces)
    else:
        return trimesh.creation.box(extents=[sx, sy, sz])


def build_tab():
    gr.Markdown("### Text-to-3D | Parametric Shapes | Boolean Ops | Multi-Format Export")
    with gr.Row():
        with gr.Column(scale=6):
            s_3d = gr.Model3D(label="3D Viewport", height=480)
            with gr.Row():
                s_file = gr.File(label="Download Model")
            s_export_fmt = gr.Dropdown(
                choices=list(EXPORT_FORMATS.keys()),
                value="STL",
                label="Export Format",
            )
            s_export_btn = gr.Button("Export Selected Format", size="sm")
        with gr.Column(scale=4):
            s_mode = gr.Radio(["Parametric Shape", "Text to 3D", "Image to 3D", "Boolean Operations"],
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

            with gr.Group(visible=False) as s_bool:
                gr.Markdown("**Shape A**")
                s_ba_shape = gr.Dropdown(
                    ["Cube", "Sphere", "Cylinder", "Cone", "Torus"],
                    value="Cube", label="Shape A")
                with gr.Row():
                    s_ba_x = gr.Slider(0.5, 20, value=3, step=0.5, label="AX")
                    s_ba_y = gr.Slider(0.5, 20, value=3, step=0.5, label="AY")
                    s_ba_z = gr.Slider(0.5, 20, value=3, step=0.5, label="AZ")
                gr.Markdown("**Shape B**")
                s_bb_shape = gr.Dropdown(
                    ["Cube", "Sphere", "Cylinder", "Cone", "Torus"],
                    value="Sphere", label="Shape B")
                with gr.Row():
                    s_bb_x = gr.Slider(0.5, 20, value=5, step=0.5, label="BX")
                    s_bb_y = gr.Slider(0.5, 20, value=5, step=0.5, label="BY")
                    s_bb_z = gr.Slider(0.5, 20, value=5, step=0.5, label="BZ")
                s_bop = gr.Radio(["Union", "Subtract (A - B)", "Intersect"],
                                 value="Union", label="Operation")
                s_bbtn = gr.Button("Compute Boolean", variant="primary")

            s_btn = gr.Button("Generate 3D Model", variant="primary", size="lg")
            s_info = gr.Markdown(label="Model Info", value="Choose a shape and click Generate.")
            s_aibtn = gr.Button("\U0001f916 AI 3D Design Assistant", size="sm")
            s_aiout = gr.Markdown()

    s_vars = [s_param, s_text, s_img, s_bool]

    def _switch(mode):
        return (gr.update(visible=mode == "Parametric Shape"),
                gr.update(visible=mode == "Text to 3D"),
                gr.update(visible=mode == "Image to 3D"),
                gr.update(visible=mode == "Boolean Operations"))

    s_mode.change(_switch, [s_mode], s_vars)

    _last_mesh = {"mesh": None}

    def _run(mode, shape, sx, sy, sz, sub, prompt, image):
        if mode == "Parametric Shape":
            glb, stl, info = generate_shape(shape, sx, sy, sz, int(sub))
        else:
            glb, stl, info = process_blueprint(prompt, image, mode)
        if glb:
            try:
                _last_mesh["mesh"] = trimesh.load(glb)
            except Exception:
                _last_mesh["mesh"] = None
        return glb, stl, info

    s_btn.click(_run,
                [s_mode, s_shape, s_sx, s_sy, s_sz, s_sub, s_prompt, s_image],
                [s_3d, s_file, s_info])

    def _run_boolean(ba, bax, bay, baz, bb, bbx, bby, bbz, op):
        try:
            mesh_a = _gen_shape(ba, bax, bay, baz, 16)
            mesh_b = _gen_shape(bb, bbx, bby, bbz, 16)
            mesh_b.apply_translation([(bbx - bax) / 2, 0, 0])
            if op == "Union":
                result = trimesh.boolean.union([mesh_a, mesh_b], engine="scad")
            elif op == "Subtract (A - B)":
                result = trimesh.boolean.difference([mesh_a, mesh_b], engine="scad")
            else:
                result = trimesh.boolean.intersection([mesh_a, mesh_b], engine="scad")
            trimesh.repair.fill_holes(result)
            trimesh.repair.fix_normals(result)
            glb = create_ephemeral_file(result, "GLB")
            stl = create_ephemeral_file(result, "STL")
            _last_mesh["mesh"] = result
            info = (f"**{op}**\n\n"
                    f"**Vertices:** {len(result.vertices):,} | **Faces:** {len(result.faces):,}\n\n"
                    f"**Volume:** {result.volume:.4f} | **Watertight:** {result.is_watertight}")
            return glb, stl, info
        except Exception as e:
            return None, None, f"**Boolean error:** {str(e)}"

    s_bbtn.click(_run_boolean,
                 [s_ba_shape, s_ba_x, s_ba_y, s_ba_z,
                  s_bb_shape, s_bb_x, s_bb_y, s_bb_z, s_bop],
                 [s_3d, s_file, s_info])

    def _export_as(fmt):
        if _last_mesh["mesh"] is None:
            return None
        return create_ephemeral_file(_last_mesh["mesh"], fmt)

    s_export_btn.click(_export_as, [s_export_fmt], [s_file])

    s_aibtn.click(
        lambda info: groq_query(
            f"Suggest improvements or variations for this 3D model: {info}",
            "You are a 3D modeling and CAD expert."),
        [s_info], [s_aiout],
    )
