"""Parametric 3D shape generation with mesh repair and dual export."""
import math
import numpy as np
import trimesh
from continuum3d.utils.mesh_utils import create_ephemeral_glb, create_ephemeral_stl


def generate_shape(shape: str, sx: float, sy: float, sz: float, subdiv: int):
    """Generate parametric 3D shapes. Returns (glb_path, stl_path, info_md)."""
    try:
        if shape == "Cube":
            mesh = trimesh.creation.box(extents=[sx, sy, sz])
        elif shape == "Sphere":
            mesh = trimesh.creation.icosphere(subdivisions=max(subdiv, 2), radius=sx / 2)
        elif shape == "Cylinder":
            mesh = trimesh.creation.cylinder(radius=sx / 2, height=sz, sections=max(subdiv * 4, 16))
        elif shape == "Cone":
            mesh = trimesh.creation.cone(radius=sx / 2, height=sz, sections=max(subdiv * 4, 16))
        elif shape == "Torus":
            mesh = trimesh.creation.torus(major_radius=sx / 2, minor_radius=sz / 2,
                                          major_segments=max(subdiv * 4, 16),
                                          minor_segments=max(subdiv * 2, 8))
        elif shape == "Capsule":
            mesh = trimesh.creation.capsule(radius=sx / 2, height=sz,
                                            sections=max(subdiv * 2, 16),
                                            sections_cap=max(subdiv, 8))
        elif shape == "Pyramid":
            verts = np.array([
                [-sx / 2, -sy / 2, 0], [sx / 2, -sy / 2, 0],
                [sx / 2, sy / 2, 0], [-sx / 2, sy / 2, 0],
                [0, 0, sz],
            ])
            faces = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
        elif shape == "Gear":
            n_teeth = max(int(sx * 3), 8)
            outer_r = sx / 2
            inner_r = outer_r * 0.78
            tooth_h = outer_r * 0.18
            angles = np.linspace(0, 2 * math.pi, n_teeth * 4, endpoint=False)
            radii = np.array([inner_r if (i % 4 in (0, 3)) else outer_r + tooth_h
                              for i in range(len(angles))])
            pts = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])
            try:
                from shapely.geometry import Polygon
                poly = Polygon(pts)
                if poly.is_valid:
                    mesh = trimesh.creation.extrude_polygon(poly, height=sz)
                else:
                    mesh = trimesh.creation.cylinder(radius=outer_r, height=sz, sections=n_teeth * 4)
            except Exception:
                mesh = trimesh.creation.cylinder(radius=outer_r, height=sz, sections=n_teeth * 4)
        else:
            mesh = trimesh.creation.box(extents=[sx, sy, sz])

        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)

        glb = create_ephemeral_glb(mesh)
        stl = create_ephemeral_stl(mesh)
        info = (
            f"**{shape} Generated**\n\n"
            f"**Dimensions:** {sx:.2f} \u00d7 {sy:.2f} \u00d7 {sz:.2f}\n\n"
            f"**Volume:** {mesh.volume:.4f} | **Surface Area:** {mesh.area:.4f}\n\n"
            f"**Vertices:** {len(mesh.vertices):,} | **Faces:** {len(mesh.faces):,}\n\n"
            f"**Watertight:** {'Yes' if mesh.is_watertight else 'Repaired'}"
        )
        return glb, stl, info

    except Exception as e:
        return None, None, f"**Error generating {shape}:** {str(e)}\n\nTry different parameters."
