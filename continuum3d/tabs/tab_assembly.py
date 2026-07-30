"""Assembly Tab — multi-body composition and transform controls."""
import gradio as gr
import trimesh
from continuum3d.engines.assembly import Assembly
from continuum3d.utils.mesh_utils import EXPORT_FORMATS

BODY_SHAPES = ["Cube", "Sphere", "Cylinder", "Cone", "Torus"]


def _make_shape(name, size):
    s = size / 2
    if name == "Cube":
        return trimesh.creation.box(extents=[size, size, size])
    elif name == "Sphere":
        return trimesh.creation.icosphere(subdivisions=3, radius=s)
    elif name == "Cylinder":
        return trimesh.creation.cylinder(radius=s, height=size, sections=16)
    elif name == "Cone":
        return trimesh.creation.cone(radius=s, height=size, sections=16)
    elif name == "Torus":
        return trimesh.creation.torus(major_radius=size / 2, minor_radius=size / 4,
                                      major_segments=16, minor_segments=8)
    return trimesh.creation.box(extents=[size, size, size])


def build_tab():
    gr.Markdown("### Multi-Body Assembly — Add, Position, Rotate")
    with gr.Row():
        with gr.Column(scale=6):
            a_3d = gr.Model3D(label="Assembly Viewport", height=480)
            with gr.Row():
                a_export_fmt = gr.Dropdown(
                    choices=list(EXPORT_FORMATS.keys()), value="STL", label="Format")
                a_export_btn = gr.Button("Export Assembly", size="sm", variant="primary")
                a_file = gr.File(label="Download")
        with gr.Column(scale=4):
            a_body_list = gr.Dataframe(
                headers=["#", "Name", "Size", "X", "Y", "Z", "RX", "RY", "RZ"],
                datatype=["number", "str", "number",
                          "number", "number", "number",
                          "number", "number", "number"],
                row_count=(3, "fixed"),
                col_count=(9, "fixed"),
                label="Body List (edit inline)",
                value=[[1, "Body1", 2, 0, 0, 0, 0, 0, 0],
                       [2, "Body2", 1.5, 3, 0, 0, 0, 0, 0],
                       [3, "Body3", 1, -3, 0, 0, 0, 0, 0]],
            )
            with gr.Row():
                a_add_shape = gr.Dropdown(BODY_SHAPES, value="Cube", label="Shape")
                a_add_btn = gr.Button("Add Body", size="sm")
            a_remove_idx = gr.Number(value=1, label="Remove body #", minimum=1, maximum=20, step=1)
            a_remove_btn = gr.Button("Remove Selected", size="sm", variant="stop")
            a_update_btn = gr.Button("Update View", variant="primary", size="lg")
            a_info = gr.Markdown("_Add bodies and click update._")

    _assembly = Assembly()

    def _add_body(shape_name, data):
        t = _assembly.add_body(shape_name, _make_shape(shape_name, 2))
        rows = [[i + 1, b.name, 2,
                 b.position[0], b.position[1], b.position[2],
                 b.rotation[0], b.rotation[1], b.rotation[2]]
                for i, b in enumerate(_assembly.bodies)]
        return rows, _assembly.summary()

    def _remove_body(idx, data):
        _assembly.remove_body(int(idx) - 1)
        rows = [[i + 1, b.name, 2,
                 b.position[0], b.position[1], b.position[2],
                 b.rotation[0], b.rotation[1], b.rotation[2]]
                for i, b in enumerate(_assembly.bodies)]
        return rows, _assembly.summary()

    def _render_from_data(data):
        _assembly.bodies.clear()
        for row in data:
            if row[1] and row[2]:
                name = str(row[1])
                size = float(row[2])
                mesh = _make_shape(row[1], size)
                idx = _assembly.add_body(name, mesh)
                _assembly.update_position(idx, float(row[3]), float(row[4]), float(row[5]))
                _assembly.update_rotation(idx, float(row[6]), float(row[7]), float(row[8]))
        combined = _assembly.render()
        if combined is None:
            return None, "_Empty assembly._"
        glb = _assembly.export("GLB")
        return glb, _assembly.summary()

    a_update_btn.click(_render_from_data, [a_body_list], [a_3d, a_info])
    a_add_btn.click(_add_body, [a_add_shape, a_body_list], [a_body_list, a_info])
    a_remove_btn.click(_remove_body, [a_remove_idx, a_body_list], [a_body_list, a_info])

    def _export_assembly(fmt):
        combined = _assembly.render()
        if combined is None:
            return None
        from continuum3d.utils.mesh_utils import create_ephemeral_file
        return create_ephemeral_file(combined, fmt)

    a_export_btn.click(_export_assembly, [a_export_fmt], [a_file])
