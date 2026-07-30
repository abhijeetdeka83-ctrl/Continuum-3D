"""Multi-body assembly operations."""
import trimesh
import numpy as np
from continuum3d.utils.mesh_utils import create_ephemeral_file


class AssemblyBody:
    def __init__(self, name: str, mesh: trimesh.Trimesh):
        self.name = name
        self.mesh = mesh.copy()
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = np.array([0.0, 0.0, 0.0])  # euler degrees

    def apply_transform(self):
        m = self.mesh.copy()
        m.apply_translation(self.position)
        rot = np.radians(self.rotation)
        m.apply_transform(trimesh.transformations.rotation_matrix(rot[2], [0, 0, 1]))
        m.apply_transform(trimesh.transformations.rotation_matrix(rot[1], [0, 1, 0]))
        m.apply_transform(trimesh.transformations.rotation_matrix(rot[0], [1, 0, 0]))
        return m


class Assembly:
    def __init__(self):
        self.bodies: list[AssemblyBody] = []

    def add_body(self, name: str, mesh: trimesh.Trimesh):
        body = AssemblyBody(name, mesh)
        self.bodies.append(body)
        return len(self.bodies) - 1

    def remove_body(self, index: int):
        if 0 <= index < len(self.bodies):
            del self.bodies[index]

    def update_position(self, index: int, x, y, z):
        if 0 <= index < len(self.bodies):
            self.bodies[index].position = np.array([x, y, z])

    def update_rotation(self, index: int, rx, ry, rz):
        if 0 <= index < len(self.bodies):
            self.bodies[index].rotation = np.array([rx, ry, rz])

    def render(self):
        if not self.bodies:
            return None
        meshes = [b.apply_transform() for b in self.bodies]
        combined = trimesh.util.concatenate(meshes)
        return combined

    def export(self, fmt: str):
        combined = self.render()
        if combined is None:
            return None
        return create_ephemeral_file(combined, fmt)

    def summary(self):
        if not self.bodies:
            return "_Empty assembly._"
        lines = [f"**Assembly: {len(self.bodies)} body(ies)**"]
        total_v = sum(len(b.mesh.vertices) for b in self.bodies)
        total_f = sum(len(b.mesh.faces) for b in self.bodies)
        for i, b in enumerate(self.bodies):
            pos = b.position
            lines.append(f"- **{b.name}** — pos({pos[0]:.1f},{pos[1]:.1f},{pos[2]:.1f}) "
                         f"| {len(b.mesh.vertices)}v {len(b.mesh.faces)}f")
        lines.append(f"**Total:** {total_v:,} vertices, {total_f:,} faces")
        return "\n".join(lines)
