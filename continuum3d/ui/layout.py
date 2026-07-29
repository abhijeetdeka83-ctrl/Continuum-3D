"""Application layout builder — assembles Gradio Blocks with all tabs."""
import gradio as gr
from continuum3d.config import APP_TITLE, CSS, HEADER_HTML, PRIMARY_HUE, SECONDARY_HUE, NEUTRAL_HUE
from continuum3d.utils.units import UNIT_TABLES
from continuum3d.tabs import (
    tab_general, tab_traditional, tab_advanced,
    tab_adaptive, tab_complex, tab_futuristic, tab_sandbox,
)


def build_theme():
    """Build custom dark-slate Gradio theme."""
    theme = gr.themes.Slate(primary_hue=PRIMARY_HUE, secondary_hue=SECONDARY_HUE, neutral_hue=NEUTRAL_HUE)
    theme = theme.set(
        body_background_fill="#0f172a",
        body_background_fill_dark="#0f172a",
        block_background_fill="#1e293b",
        block_background_fill_dark="#1e293b",
        block_border_color="#334155",
        block_border_color_dark="#334155",
        block_label_text_color="#94a3b8",
        block_label_text_color_dark="#94a3b8",
        block_title_text_color="#e2e8f0",
        block_title_text_color_dark="#e2e8f0",
        input_background_fill="#0f172a",
        input_background_fill_dark="#0f172a",
        input_border_color="#475569",
        input_border_color_dark="#475569",
        button_primary_background_fill="#3b82f6",
        button_primary_background_fill_dark="#3b82f6",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        slider_color="#3b82f6",
        slider_color_dark="#3b82f6",
        text_color="#e2e8f0",
        text_color_dark="#e2e8f0",
    )
    return theme


def build_app() -> gr.Blocks:
    """Construct the full Continuum 3D Gradio application."""
    theme = build_theme()

    with gr.Blocks(theme=theme, title=APP_TITLE, css=CSS) as app:
        gr.Markdown(HEADER_HTML)

        with gr.Tabs():
            with gr.Tab("General"):
                tab_general.build_tab()
            with gr.Tab("Traditional"):
                tab_traditional.build_tab()
            with gr.Tab("Advanced"):
                tab_advanced.build_tab()
            with gr.Tab("Adaptive"):
                tab_adaptive.build_tab()
            with gr.Tab("Complex"):
                tab_complex.build_tab()
            with gr.Tab("Futuristic"):
                tab_futuristic.build_tab()
            with gr.Tab("Custom 3D Sandbox"):
                tab_sandbox.build_tab()

    return app
