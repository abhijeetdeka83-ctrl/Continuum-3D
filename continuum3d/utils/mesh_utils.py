"""Ephemeral mesh file management — zero storage, tempfile-based."""
import math
import tempfile
from typing import Optional

import numpy as np
import trimesh


def create_ephemeral_stl(mesh: trimesh.Trimesh) -> Optional[str]:
    """Create a temporary binary STL with mesh repair (fill holes, fix normals)."""
    try:
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)
        tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False, dir=tempfile.gettempdir())
        mesh.export(tmp.name, file_type="stl")
        tmp.close()
        return tmp.name
    except Exception:
        return None


def create_ephemeral_glb(mesh: trimesh.Trimesh) -> Optional[str]:
    """Create a temporary GLB file for the interactive 3D viewport."""
    try:
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)
        tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False, dir=tempfile.gettempdir())
        mesh.export(tmp.name, file_type="glb")
        tmp.close()
        return tmp.name
    except Exception:
        return None


def create_strut(p1, p2, radius: float) -> Optional[trimesh.Trimesh]:
    """Create a cylinder (strut) between two 3D points for lattice generation."""
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    direction = p2 - p1
    length = float(np.linalg.norm(direction))
    if length < 1e-10:
        return None
    center = (p1 + p2) / 2.0
    cylinder = trimesh.creation.cylinder(radius=radius, height=length)
    z_axis = np.array([0.0, 0.0, 1.0])
    direction_norm = direction / length
    cos_angle = np.clip(np.dot(z_axis, direction_norm), -1.0, 1.0)
    if cos_angle < -0.9999:
        cylinder.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    elif cos_angle < 0.9999:
        rot_axis = np.cross(z_axis, direction_norm)
        rot_axis_norm = np.linalg.norm(rot_axis)
        if rot_axis_norm > 1e-10:
            cylinder.apply_transform(
                trimesh.transformations.rotation_matrix(math.acos(cos_angle), rot_axis / rot_axis_norm)
            )
    cylinder.apply_translation(center)
    return cylinder


def repair_and_export(mesh: trimesh.Trimesh):
    """Repair mesh and return both GLB and STL ephemeral paths."""
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    return create_ephemeral_glb(mesh), create_ephemeral_stl(mesh)
