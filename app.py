"""
Continuum 3D — Entry Point
Zero-Storage Interactive 3D Engineering Workspace & Generative CAD Studio
"""
from continuum3d.ui.layout import build_app
from continuum3d.config import SERVER_NAME, SERVER_PORT, GRADIO_SHARE

if __name__ == "__main__":
    demo = build_app()
    demo.launch(server_name=SERVER_NAME, server_port=SERVER_PORT, share=GRADIO_SHARE)
