"""History manager — undo/redo for mesh operations + session save/load."""
import json
import tempfile
import os
import trimesh
import numpy as np


class MeshHistory:
    def __init__(self, max_steps: int = 50):
        self.stack: list[dict] = []
        self.pos = -1
        self.max_steps = max_steps

    def push(self, vertices, faces):
        entry = {
            "vertices": vertices.tolist() if isinstance(vertices, np.ndarray) else vertices,
            "faces": faces.tolist() if isinstance(faces, np.ndarray) else faces,
            "timestamp": __import__("time").time(),
        }
        self.stack = self.stack[:self.pos + 1]
        self.stack.append(entry)
        if len(self.stack) > self.max_steps:
            self.stack.pop(0)
        self.pos = len(self.stack) - 1

    def undo(self):
        if self.pos > 0:
            self.pos -= 1
            return self._entry_to_mesh(self.stack[self.pos])
        return None

    def redo(self):
        if self.pos < len(self.stack) - 1:
            self.pos += 1
            return self._entry_to_mesh(self.stack[self.pos])
        return None

    def current(self):
        if 0 <= self.pos < len(self.stack):
            return self._entry_to_mesh(self.stack[self.pos])
        return None

    def can_undo(self):
        return self.pos > 0

    def can_redo(self):
        return self.pos < len(self.stack) - 1

    @staticmethod
    def _entry_to_mesh(entry):
        return trimesh.Trimesh(
            vertices=np.array(entry["vertices"]),
            faces=np.array(entry["faces"]),
        )

    def export_session(self) -> str:
        data = {
            "version": 1,
            "stack": self.stack,
            "pos": self.pos,
        }
        path = os.path.join(tempfile.gettempdir(), "continuum3d_session.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    @classmethod
    def import_session(cls, path: str):
        with open(path) as f:
            data = json.load(f)
        h = cls()
        h.stack = data["stack"]
        h.pos = data["pos"]
        return h
