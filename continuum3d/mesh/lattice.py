"""3D lattice structure generation (Cubic, BCC, Octet)."""
import numpy as np
import trimesh
from continuum3d.utils.mesh_utils import create_strut, create_ephemeral_glb, create_ephemeral_stl


def generate_lattice(lattice_type: str, cell_size: float, nx: int, ny: int, nz: int,
                     strut_radius: float):
    """Generate 3D lattice structures. Returns (glb_path, stl_path, info_md)."""
    meshes = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                origin = np.array([i * cell_size, j * cell_size, k * cell_size])
                if lattice_type == "Cubic":
                    if i < nx - 1:
                        s = create_strut(origin, origin + [cell_size, 0, 0], strut_radius)
                        if s:
                            meshes.append(s)
                    if j < ny - 1:
                        s = create_strut(origin, origin + [0, cell_size, 0], strut_radius)
                        if s:
                            meshes.append(s)
                    if k < nz - 1:
                        s = create_strut(origin, origin + [0, 0, cell_size], strut_radius)
                        if s:
                            meshes.append(s)
                elif lattice_type == "BCC":
                    center = origin + cell_size / 2
                    for dx in (-1, 1):
                        for dy in (-1, 1):
                            for dz in (-1, 1):
                                neighbor = origin + cell_size / 2 + np.array([dx, dy, dz]) * cell_size / 2
                                s = create_strut(center, neighbor, strut_radius)
                                if s:
                                    meshes.append(s)
                elif lattice_type == "Octet":
                    center = origin + cell_size / 2
                    face_offsets = [
                        [cell_size, 0, 0], [-cell_size, 0, 0],
                        [0, cell_size, 0], [0, -cell_size, 0],
                        [0, 0, cell_size], [0, 0, -cell_size],
                    ]
                    for fo in face_offsets:
                        s = create_strut(center, center + np.array(fo) / 2, strut_radius)
                        if s:
                            meshes.append(s)

    if not meshes:
        return None, None, "No mesh generated. Check parameters."

    combined = trimesh.util.concatenate(meshes)
    glb = create_ephemeral_glb(combined)
    stl = create_ephemeral_stl(combined)
    bmin, bmax = combined.bounds
    bbox_size = bmax - bmin
    info = (
        f"**Lattice: {lattice_type}**\n\n"
        f"**Grid:** {nx}\u00d7{ny}\u00d7{nz} | **Cell:** {cell_size} m | **Strut r:** {strut_radius} m\n\n"
        f"**Bounding Box:** [{bbox_size[0]:.3f}, {bbox_size[1]:.3f}, {bbox_size[2]:.3f}] m\n\n"
        f"**Triangles:** {len(combined.faces):,} | **Vertices:** {len(combined.vertices):,}\n\n"
        f"**Watertight:** {'Yes' if combined.is_watertight else 'No (repair attempted)'}"
    )
    return glb, stl, info
