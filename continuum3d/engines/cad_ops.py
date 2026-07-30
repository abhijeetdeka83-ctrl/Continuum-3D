"""CAD sweep, loft, and revolve operations."""
import trimesh
import numpy as np
from shapely.geometry import Polygon, Point
from continuum3d.utils.mesh_utils import create_ephemeral_file


def revolve_profile(points_2d: list[tuple[float, float]], angle_deg: float = 360, sections: int = 32):
    """Revolve a 2D profile around the Z-axis."""
    if len(points_2d) < 3:
        return None
    poly = Polygon(points_2d)
    if not poly.is_valid or poly.area < 1e-6:
        return None
    angle = np.radians(min(angle_deg, 360))
    n = max(int(sections * angle / (2 * np.pi)), 4) if angle < 2 * np.pi else sections
    theta = np.linspace(0, angle, n + 1)
    verts = []
    faces = []
    for i, pt in enumerate(points_2d):
        for j, t in enumerate(theta):
            x = pt[0] * np.cos(t)
            y = pt[0] * np.sin(t)
            z = pt[1]
            verts.append([x, y, z])
    for i in range(len(points_2d) - 1):
        for j in range(n):
            a = i * (n + 1) + j
            b = a + 1
            c = (i + 1) * (n + 1) + j
            d = c + 1
            faces.append([a, b, d])
            faces.append([a, d, c])
    return trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces))


def sweep_profile(points_2d: list[tuple[float, float]], path: list[tuple[float, float, float]]):
    """Sweep a 2D profile along a 3D path."""
    if len(points_2d) < 3 or len(path) < 2:
        return None
    poly = Polygon(points_2d)
    if not poly.is_valid:
        return None
    extrusions = []
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        dz = path[i + 1][2] - path[i][2]
        seg_len = np.sqrt(dx * dx + dy * dy + dz * dz)
        if seg_len < 1e-6:
            continue
        center = [(path[i][0] + path[i + 1][0]) / 2,
                  (path[i][1] + path[i + 1][1]) / 2,
                  (path[i][2] + path[i + 1][2]) / 2]
        pts_3d = [[p[0] + center[0], p[1] + center[1], center[2]] for p in points_2d]
        m = trimesh.Trimesh(
            vertices=np.array(pts_3d + [[p[0] + center[0], p[1] + center[1], center[2] + seg_len]
                                        for p in points_2d]),
            faces=[],
        )
        verts = np.array([
            [p[0] + center[0], p[1] + center[1], center[2]]
            for p in points_2d
        ] + [
            [p[0] + center[0], p[1] + center[1], center[2] + seg_len]
            for p in points_2d
        ])
        n = len(points_2d)
        tris = []
        for i in range(n):
            a = i
            b = (i + 1) % n
            c = n + i
            d = n + (i + 1) % n
            tris.append([a, b, d])
            tris.append([a, d, c])
        base = [n - 1 - i for i in range(n)]
        top = [n + i for i in range(n)]
        m = trimesh.Trimesh(vertices=verts, faces=tris + [base] + [top])
        extrusions.append(m)
    if not extrusions:
        return None
    return trimesh.util.concatenate(extrusions)


def loft_profiles(profiles: list[list[tuple[float, float]]], heights: list[float]):
    """Loft between 2D profiles at different heights."""
    if len(profiles) < 2 or len(profiles) != len(heights):
        return None
    all_verts = []
    all_faces = []
    offset = 0
    for layer, (pts, h) in enumerate(zip(profiles, heights)):
        for p in pts:
            all_verts.append([p[0], p[1], h])
        if layer > 0:
            prev_n = len(profiles[layer - 1])
            cur_n = len(pts)
            for i in range(prev_n):
                a = offset - prev_n + i
                b = offset - prev_n + (i + 1) % prev_n
                c_idx = min(i, cur_n - 1)
                d_idx = min((i + 1) % cur_n, cur_n - 1)
                c = offset + c_idx
                d = offset + d_idx
                all_faces.append([a, b, d])
                all_faces.append([a, d, c])
        offset += len(pts)
    return trimesh.Trimesh(vertices=np.array(all_verts), faces=np.array(all_faces))
