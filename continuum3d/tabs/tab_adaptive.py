"""Tab 4: Adaptive — Lattices, FEA."""
import gradio as gr
from continuum3d.mesh.lattice import generate_lattice
from continuum3d.engines.fea import fea_heatmap


def build_tab():
    gr.Markdown("### Smart Materials, FEA & Lattice Structures")
    with gr.Row():
        with gr.Column(scale=6):
            ad_plot = gr.Plot(label="FEA / Analysis", show_label=False)
            ad_3d = gr.Model3D(label="3D Viewport", height=350)
            ad_file = gr.File(label="Download STL")
        with gr.Column(scale=4):
            ad_mode = gr.Radio(["Lattice Generator", "FEA Heatmap"],
                               value="Lattice Generator", label="Mode")

            with gr.Group() as ad_lat:
                ad_ltype = gr.Dropdown(["Cubic", "BCC", "Octet"], value="Cubic", label="Type")
                ad_cell = gr.Slider(0.5, 5, value=2.0, step=0.1, label="Cell Size (m)")
                ad_nx = gr.Slider(1, 8, value=3, step=1, label="X Cells")
                ad_ny = gr.Slider(1, 8, value=3, step=1, label="Y Cells")
                ad_nz = gr.Slider(1, 8, value=2, step=1, label="Z Cells")
                ad_strut = gr.Slider(0.01, 0.3, value=0.08, step=0.01, label="Strut Radius (m)")

            with gr.Group(visible=False) as ad_fea:
                ad_ftype = gr.Dropdown(["Point Load (Center)", "Distributed Load",
                                        "Cantilever Tip", "Torsion"],
                                       value="Point Load (Center)", label="Load Type")
                ad_fmax = gr.Slider(1e3, 1e9, value=1e6, step=1e3, label="Max Stress (Pa)")
                ad_fnum = gr.Slider(64, 2500, value=400, step=64, label="Elements")

            ad_btn = gr.Button("Generate", variant="primary")
            ad_info = gr.Markdown(label="Info")

    def _switch(mode):
        return gr.update(visible=mode == "Lattice Generator"), \
               gr.update(visible=mode == "FEA Heatmap")

    ad_mode.change(_switch, [ad_mode], [ad_lat, ad_fea])

    def _run(mode, lt, cell, nx, ny, nz, strut, ft, fmax, fnum):
        if mode == "Lattice Generator":
            glb, stl, info = generate_lattice(lt, cell, int(nx), int(ny), int(nz), strut)
            return None, glb, stl, info
        fig, info = fea_heatmap(ft, fmax, int(fnum))
        return fig, None, None, info

    ad_btn.click(_run,
                 [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                  ad_ftype, ad_fmax, ad_fnum],
                 [ad_plot, ad_3d, ad_file, ad_info])
    ad_mode.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                          ad_ftype, ad_fmax, ad_fnum],
                   [ad_plot, ad_3d, ad_file, ad_info])
    ad_ltype.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                           ad_ftype, ad_fmax, ad_fnum],
                    [ad_plot, ad_3d, ad_file, ad_info])
    ad_cell.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                          ad_ftype, ad_fmax, ad_fnum],
                   [ad_plot, ad_3d, ad_file, ad_info])
    ad_nx.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                        ad_ftype, ad_fmax, ad_fnum],
                 [ad_plot, ad_3d, ad_file, ad_info])
    ad_ny.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                        ad_ftype, ad_fmax, ad_fnum],
                 [ad_plot, ad_3d, ad_file, ad_info])
    ad_nz.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                        ad_ftype, ad_fmax, ad_fnum],
                 [ad_plot, ad_3d, ad_file, ad_info])
    ad_strut.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                           ad_ftype, ad_fmax, ad_fnum],
                    [ad_plot, ad_3d, ad_file, ad_info])
    ad_ftype.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                           ad_ftype, ad_fmax, ad_fnum],
                    [ad_plot, ad_3d, ad_file, ad_info])
    ad_fmax.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                          ad_ftype, ad_fmax, ad_fnum],
                   [ad_plot, ad_3d, ad_file, ad_info])
    ad_fnum.change(_run, [ad_mode, ad_ltype, ad_cell, ad_nx, ad_ny, ad_nz, ad_strut,
                          ad_ftype, ad_fmax, ad_fnum],
                   [ad_plot, ad_3d, ad_file, ad_info])
