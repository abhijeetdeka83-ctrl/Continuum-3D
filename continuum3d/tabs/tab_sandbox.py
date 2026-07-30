"""Tab 7: Custom 3D Sandbox — Parametric, CAD ops, Multi-Format Export."""
import gradio as gr
import trimesh
import numpy as np
from continuum3d.mesh.shapes import generate_shape
from continuum3d.mesh.blueprint import process_blueprint
from continuum3d.utils.groq_client import groq_query
from continuum3d.utils.mesh_utils import EXPORT_FORMATS, create_ephemeral_file
from continuum3d.utils.history import MeshHistory
from continuum3d.engines.cad_ops import revolve_profile, loft_profiles


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


def _shell_mesh(mesh, thickness):
    try:
        result = mesh.copy()
        hollow = trimesh.creation.box(extents=result.extents - thickness * 2)
        result = trimesh.boolean.difference([result, hollow], engine="scad")
        trimesh.repair.fill_holes(result)
        trimesh.repair.fix_normals(result)
        return result
    except Exception:
        return mesh


def _pattern_mesh(mesh, count_x, count_y, spacing):
    meshes = []
    for i in range(int(count_x)):
        for j in range(int(count_y)):
            copy = mesh.copy()
            copy.apply_translation([i * spacing, j * spacing, 0])
            meshes.append(copy)
    return trimesh.util.concatenate(meshes)


def _revolve_profile(profile_points, angle_deg, steps):
    angle = np.radians(min(angle_deg, 360))
    pts = np.array(profile_points)
    if len(pts) < 3:
        return trimesh.creation.cylinder(radius=1, height=2)
    poly = trimesh.path.polygons.Polygon(pts)
    if not poly.is_valid:
        return trimesh.creation.cylinder(radius=1, height=2)
    return trimesh.creation.extrude_polygon(poly, height=2)


def build_tab():
    gr.Markdown("### Parametric Shapes | CAD Ops | Text-to-3D | Multi-Format Export")
    with gr.Row():
        with gr.Column(scale=6):
            s_3d = gr.Model3D(label="3D Viewport", height=480)
            with gr.Row():
                s_file = gr.File(label="Download Model")
            with gr.Row():
                s_undo_btn = gr.Button("\u21a9 Undo", size="sm")
                s_redo_btn = gr.Button("\u21aa Redo", size="sm")
                s_save_btn = gr.Button("\U0001f4be Save Session", size="sm")
                s_load_btn = gr.Button("\U0001f4c2 Load Session", size="sm")
            s_export_fmt = gr.Dropdown(
                choices=list(EXPORT_FORMATS.keys()), value="STL", label="Export Format",
            )
            s_export_btn = gr.Button("Export Selected Format", size="sm")
            s_session_file = gr.File(label="Session File", visible=False)
        with gr.Column(scale=4):
            s_mode = gr.Radio(
                ["Parametric Shape", "Text to 3D", "Image to 3D",
                 "Boolean Operations", "Shell / Hollow",
                 "Linear Pattern", "Import Mesh",
                 "Revolve", "Loft"],
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

            with gr.Group(visible=False) as s_shell:
                s_sh_shape = gr.Dropdown(
                    ["Cube", "Sphere", "Cylinder"],
                    value="Cube", label="Base Shape")
                s_sh_size = gr.Slider(1, 20, value=5, step=0.5, label="Size (m)")
                s_sh_thick = gr.Slider(0.05, 2, value=0.2, step=0.05, label="Wall Thickness (m)")
                s_shbtn = gr.Button("Create Shell", variant="primary")

            with gr.Group(visible=False) as s_pat:
                s_pt_shape = gr.Dropdown(
                    ["Cube", "Sphere", "Cylinder"],
                    value="Cube", label="Base Shape")
                s_pt_size = gr.Slider(0.5, 5, value=1, step=0.5, label="Element Size")
                s_pt_cx = gr.Slider(1, 10, value=3, step=1, label="Count X")
                s_pt_cy = gr.Slider(1, 10, value=3, step=1, label="Count Y")
                s_pt_sp = gr.Slider(1, 10, value=2, step=0.5, label="Spacing")
                s_ptbtn = gr.Button("Create Pattern", variant="primary")

            with gr.Group(visible=False) as s_imp:
                s_imp_file = gr.File(label="Upload 3D Model (STL/OBJ/PLY)")
                s_impbtn = gr.Button("Load Mesh", variant="primary")

            with gr.Group(visible=False) as s_rev:
                gr.Markdown("**Revolve 2D Profile**")
                s_rev_pts = gr.Textbox(
                    label="Profile points (x,y per line)",
                    placeholder="0,0\n2,0\n2,4\n0,4",
                    value="0,0\n2,0\n2,4\n0,4", lines=4)
                s_rev_ang = gr.Slider(90, 360, value=360, step=10, label="Angle (deg)")
                s_revbtn = gr.Button("Revolve", variant="primary")

            with gr.Group(visible=False) as s_lft:
                gr.Markdown("**Loft Between Profiles**")
                s_lft_profiles = gr.Textbox(
                    label="Profiles (semicolon-separated, x,y per line)",
                    placeholder="Profile1: 0,0;1,0;1,1;0,1\n"
                                "Profile2: 0,0;2,0;2,2;0,2",
                    value="0,0;1,0;1,1;0,1\n0,0;2,0;2,2;0,2", lines=4)
                s_lftbtn = gr.Button("Loft", variant="primary")

            s_btn = gr.Button("Generate / Apply", variant="primary", size="lg")
            s_info = gr.Markdown(label="Model Info", value="Choose a mode and configure.")
            s_aibtn = gr.Button("\U0001f916 AI 3D Design Assistant", size="sm")
            s_aiout = gr.Markdown()

    s_vars = [s_param, s_text, s_img, s_bool, s_shell, s_pat, s_imp, s_rev, s_lft]

    def _switch(mode):
        return [gr.update(visible=(label == mode))
                for label in ["Parametric Shape", "Text to 3D", "Image to 3D",
                              "Boolean Operations", "Shell / Hollow",
                              "Linear Pattern", "Import Mesh",
                              "Revolve", "Loft"]]

    s_mode.change(_switch, [s_mode], s_vars)

    _last_mesh = {"mesh": None, "path": None}
    _history = MeshHistory()

    def _push_mesh(mesh):
        if mesh is not None and hasattr(mesh, "vertices") and hasattr(mesh, "faces"):
            _history.push(mesh.vertices, mesh.faces)

    def _render_history():
        mesh = _history.current()
        if mesh is None:
            return None, None, "_No mesh in history._"
        _last_mesh["mesh"] = mesh
        glb = create_ephemeral_file(mesh, "GLB")
        stl = create_ephemeral_file(mesh, "STL")
        return glb, stl, (f"Vertices: {len(mesh.vertices):,} | "
                          f"Faces: {len(mesh.faces):,} | "
                          f"History: {_history.pos + 1}/{len(_history.stack)}")

    def _run(mode, shape, sx, sy, sz, sub, prompt, image,
             ba, bax, bay, baz, bb, bbx, bby, bbz, bop,
             sh_sh, sh_sz, sh_th,
             pt_sh, pt_sz, pt_cx, pt_cy, pt_sp,
             imp_file, rev_pts, rev_ang, lft_profiles):
        try:
            if mode == "Parametric Shape":
                glb, stl, info = generate_shape(shape, sx, sy, sz, int(sub))
                if glb:
                    _push_mesh(trimesh.load(glb))
                return glb, stl, info
            elif mode == "Text to 3D" or mode == "Image to 3D":
                glb, stl, info = process_blueprint(prompt, image, mode)
                if glb:
                    _push_mesh(trimesh.load(glb))
                return glb, stl, info
            elif mode == "Boolean Operations":
                mesh_a = _gen_shape(ba, bax, bay, baz, 16)
                mesh_b = _gen_shape(bb, bbx, bby, bbz, 16)
                mesh_b.apply_translation([(bbx - bax) / 2, 0, 0])
                if bop == "Union":
                    result = trimesh.boolean.union([mesh_a, mesh_b], engine="scad")
                elif bop == "Subtract (A - B)":
                    result = trimesh.boolean.difference([mesh_a, mesh_b], engine="scad")
                else:
                    result = trimesh.boolean.intersection([mesh_a, mesh_b], engine="scad")
                _push_mesh(result)
                glb = create_ephemeral_file(result, "GLB")
                stl = create_ephemeral_file(result, "STL")
                return glb, stl, (f"**{bop}**\n\nVertices: {len(result.vertices):,} | "
                                  f"Faces: {len(result.faces):,}\n\nVolume: {result.volume:.4f}")
            elif mode == "Shell / Hollow":
                base = _gen_shape(sh_sh, sh_sz, sh_sz, sh_sz, 16)
                result = _shell_mesh(base, sh_th)
                _push_mesh(result)
                glb = create_ephemeral_file(result, "GLB")
                stl = create_ephemeral_file(result, "STL")
                return glb, stl, (f"**Shell:** {sh_sh} | Wall: {sh_th}m\n\n"
                                  f"Volume: {result.volume:.4f}")
            elif mode == "Linear Pattern":
                base = _gen_shape(pt_sh, pt_sz, pt_sz, pt_sz, 8)
                result = _pattern_mesh(base, pt_cx, pt_cy, pt_sp)
                _push_mesh(result)
                glb = create_ephemeral_file(result, "GLB")
                stl = create_ephemeral_file(result, "STL")
                return glb, stl, (f"**Pattern:** {int(pt_cx)}x{int(pt_cy)} = "
                                  f"{int(pt_cx * pt_cy)} elements\n\n"
                                  f"Volume: {result.volume:.4f}")
            elif mode == "Import Mesh":
                if imp_file and os.path.exists(imp_file):
                    result = trimesh.load(imp_file)
                    _push_mesh(result)
                    glb = create_ephemeral_file(result, "GLB")
                    stl = create_ephemeral_file(result, "STL")
                    return glb, stl, (f"**Imported:** {os.path.basename(imp_file)}\n\n"
                                      f"Vertices: {len(result.vertices):,} | "
                                      f"Faces: {len(result.faces):,}")
                return None, None, "No file uploaded."
            elif mode == "Revolve":
                pts_2d = [tuple(map(float, line.split(","))) for line in rev_pts.strip().split("\n") if line.strip()]
                result = revolve_profile(pts_2d, rev_ang)
                if result is None:
                    return None, None, "_Invalid profile (need 3+ points)._"
                _push_mesh(result)
                glb = create_ephemeral_file(result, "GLB")
                stl = create_ephemeral_file(result, "STL")
                return glb, stl, (f"**Revolve:** {rev_ang}\u00b0 | "
                                  f"{len(result.vertices):,}v {len(result.faces):,}f")
            elif mode == "Loft":
                profiles = []
                heights = []
                for i, block in enumerate(lft_profiles.strip().split("\n")):
                    block = block.strip()
                    if not block:
                        continue
                    pts = [tuple(map(float, p.split(","))) for p in block.split(";") if p.strip()]
                    if len(pts) >= 3:
                        profiles.append(pts)
                        heights.append(float(i))
                if len(profiles) < 2:
                    return None, None, "_Need at least 2 profiles with 3+ points each._"
                result = loft_profiles(profiles, heights)
                if result is None:
                    return None, None, "_Loft failed._"
                _push_mesh(result)
                glb = create_ephemeral_file(result, "GLB")
                stl = create_ephemeral_file(result, "STL")
                return glb, stl, (f"**Loft:** {len(profiles)} profiles | "
                                  f"{len(result.vertices):,}v {len(result.faces):,}f")
        except Exception as e:
            return None, None, f"**Error:** {str(e)}"

    s_btn.click(_run,
                [s_mode, s_shape, s_sx, s_sy, s_sz, s_sub, s_prompt, s_image,
                 s_ba_shape, s_ba_x, s_ba_y, s_ba_z,
                 s_bb_shape, s_bb_x, s_bb_y, s_bb_z, s_bop,
                 s_sh_shape, s_sh_size, s_sh_thick,
                 s_pt_shape, s_pt_size, s_pt_cx, s_pt_cy, s_pt_sp,
                 s_imp_file, s_rev_pts, s_rev_ang, s_lft_profiles],
                [s_3d, s_file, s_info])

    s_bbtn.click(lambda *a: _run("Boolean Operations", *a),
                 [s_ba_shape, s_ba_x, s_ba_y, s_ba_z,
                  s_bb_shape, s_bb_x, s_bb_y, s_bb_z, s_bop],
                 [s_3d, s_file, s_info])

    s_shbtn.click(lambda *a: _run("Shell / Hollow", *a),
                  [s_sh_shape, s_sh_size, s_sh_thick],
                  [s_3d, s_file, s_info])

    s_ptbtn.click(lambda *a: _run("Linear Pattern", *a),
                  [s_pt_shape, s_pt_size, s_pt_cx, s_pt_cy, s_pt_sp],
                  [s_3d, s_file, s_info])

    s_impbtn.click(lambda *a: _run("Import Mesh", *a),
                   [s_imp_file],
                   [s_3d, s_file, s_info])

    def _undo():
        mesh = _history.undo()
        _last_mesh["mesh"] = mesh
        if mesh is None:
            return None, None, "_At oldest state._"
        glb = create_ephemeral_file(mesh, "GLB")
        stl = create_ephemeral_file(mesh, "STL")
        return glb, stl, (f"**Undo** — Step {_history.pos + 1}/{len(_history.stack)}")

    def _redo():
        mesh = _history.redo()
        _last_mesh["mesh"] = mesh
        if mesh is None:
            return None, None, "_At newest state._"
        glb = create_ephemeral_file(mesh, "GLB")
        stl = create_ephemeral_file(mesh, "STL")
        return glb, stl, (f"**Redo** — Step {_history.pos + 1}/{len(_history.stack)}")

    def _save_session():
        if not _history.stack:
            return None
        path = _history.export_session()
        return path

    def _load_session(path):
        if not path:
            return None, None, "_No file selected._"
        try:
            h = MeshHistory.import_session(path)
            _history.stack = h.stack
            _history.pos = h.pos
            return _render_history()
        except Exception as e:
            return None, None, f"_Load failed: {e}_"

    s_undo_btn.click(_undo, None, [s_3d, s_file, s_info])
    s_redo_btn.click(_redo, None, [s_3d, s_file, s_info])
    s_save_btn.click(_save_session, None, [s_session_file])
    s_load_btn.click(_load_session, [s_session_file], [s_3d, s_file, s_info])

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

    # initial seed
    _push_mesh(_gen_shape("Cube", 5, 5, 5, 16))
    _render_history()
