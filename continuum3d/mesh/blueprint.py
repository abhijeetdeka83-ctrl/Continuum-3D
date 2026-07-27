"""AI-assisted 3D blueprint generation — text/image to mesh."""
import json
from continuum3d.utils.groq_client import groq_query
from continuum3d.mesh.shapes import generate_shape


def process_blueprint(prompt: str, image_input, mode: str):
    """AI-assisted 3D generation: interpret text/image and produce a mesh.
    Returns (glb_path, stl_path, info_md)."""
    system_msg = (
        "Output ONLY valid JSON with keys: "
        '"shape" (Cube|Sphere|Cylinder|Cone|Torus|Capsule|Pyramid|Gear), '
        '"sx" (float 1-20), "sy" (float 1-20), "sz" (float 1-20), '
        '"subdiv" (int 8-64). No explanation.'
    )

    if mode == "Text to 3D" and prompt.strip():
        raw = groq_query(f"Generate a 3D shape spec for: {prompt}", system_msg)
        try:
            text = raw
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            params = json.loads(text.strip())
            return generate_shape(
                params.get("shape", "Cube"),
                float(params.get("sx", 5)),
                float(params.get("sy", 5)),
                float(params.get("sz", 5)),
                int(params.get("subdiv", 16)),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            glb, stl, _ = generate_shape("Cube", 5, 5, 5, 16)
            info = (
                f"**AI Response (unstructured):**\n\n{raw}\n\n"
                f"*Could not parse structured shape \u2014 generating default cube. "
                f"Use parametric controls for precise shapes.*"
            )
            return glb, stl, info

    elif image_input is not None:
        glb, stl, _ = generate_shape("Cube", 5, 5, 5, 16)
        info = (
            "**Image Received**\n\n"
            "Image-to-3D reconstruction requires specialized vision models. "
            "Use the parametric controls to manually approximate the shape.\n\n"
            "**Tips:** Identify primitives \u2192 select shape \u2192 adjust dimensions \u2192 export STL."
        )
        return glb, stl, info

    return None, None, "Provide a text description or upload an image."
