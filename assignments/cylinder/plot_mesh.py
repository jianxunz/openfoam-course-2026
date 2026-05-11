import numpy as np
import pyvista as pv
from pathlib import Path


# =================================================
# User settings
# =================================================
vtk_dir = Path("VTK")

# Leave as None for automatic detection
internal_mesh_file = None
wall_patch_file = None

# Example manual settings:
# internal_mesh_file = Path("VTK/cylinder_0.vtk")
# wall_patch_file = Path("VTK/cylinder/cylinder_0.vtk")

# Cylinder geometry
cylinder_center = (0.0, 0.0, 0.0)
cylinder_radius = 0.5

# Figure quality
window_size = (3200, 2200)
off_screen = True

# Mesh appearance
mesh_color = "#e6e6e6"
mesh_line_color = "blue"
mesh_line_width = 2.0

# Cylinder appearance
draw_cylinder = True
cylinder_color = "dimgray"

# Output files
output_full = "mesh_full_domain.png"
output_zoom = "mesh_near_cylinder.png"

# Zoom region near cylinder
zoom_xlim = [-2.0, 3.0]
zoom_ylim = [-2.0, 2.0]


# =================================================
# Helper functions
# =================================================
def find_internal_mesh(vtk_dir):
    candidates = sorted(vtk_dir.glob("*.vtk"))
    if not candidates:
        raise FileNotFoundError(
            "No internal VTK file found directly inside VTK/.\n"
            "Run:\n"
            "  foamToVTK -time 0\n"
        )
    return candidates[-1]


def find_wall_patch(vtk_dir):
    candidates = sorted((vtk_dir / "cylinder").glob("*.vtk"))
    if not candidates:
        raise FileNotFoundError(
            "No cylinder wall patch file found.\n"
            "Expected something like:\n"
            "  VTK/cylinder/cylinder_0.vtk\n"
        )
    return candidates[-1]


def extract_midplane(mesh):
    zmin, zmax = mesh.bounds[4], mesh.bounds[5]
    zmid = 0.5 * (zmin + zmax)

    if abs(zmax - zmin) > 1e-12:
        mesh2d = mesh.slice(normal="z", origin=(0.0, 0.0, zmid))
        if mesh2d.n_cells == 0:
            mesh2d = mesh
    else:
        mesh2d = mesh

    return mesh2d, zmid


def calculate_first_cell_distance(mesh2d, wall_file, cylinder_center, zmid):
    """
    Calculate one representative first-cell distance y1.

    y1 is the wall-to-first-cell-centre distance.
    For a circular cylinder, the local wall-normal direction is radial.
    """

    cell_centres = mesh2d.cell_centers().points
    cell_xy = cell_centres[:, :2]

    wall_patch = pv.read(wall_file)
    wall_centres = wall_patch.extract_surface().cell_centers().points

    # Keep wall faces close to the plotting mid-plane
    if wall_centres.shape[1] == 3:
        z_distance = np.abs(wall_centres[:, 2] - zmid)
        z_tol = max(1e-10, 0.05 * abs(mesh2d.bounds[5] - mesh2d.bounds[4]))
        near_mid = z_distance <= z_tol

        if np.count_nonzero(near_mid) > 0:
            wall_centres = wall_centres[near_mid]

    wall_xy = wall_centres[:, :2]

    xc, yc, _ = cylinder_center
    centre_xy = np.array([xc, yc])

    y1_values = []

    for x_wall in wall_xy:
        radial = x_wall - centre_xy
        radial_norm = np.linalg.norm(radial)

        if radial_norm < 1e-14:
            continue

        normal = radial / radial_norm

        vec = cell_xy - x_wall
        normal_distance = vec @ normal

        # Only cells outside the cylinder wall
        candidates = np.where(normal_distance > 1e-14)[0]
        if candidates.size == 0:
            continue

        # Nearest fluid cell centre to this wall face
        distance_to_wall = np.linalg.norm(vec[candidates], axis=1)
        nearest_cell = candidates[np.argmin(distance_to_wall)]

        y1_values.append(normal_distance[nearest_cell])

    if not y1_values:
        raise RuntimeError("Could not calculate first-cell distance near the cylinder.")

    # The first layer is uniform, so one representative value is enough
    return float(np.median(y1_values))


def plot_mesh(mesh2d, zmid, mesh_info, output_png, xlim=None, ylim=None):
    plotter = pv.Plotter(
        off_screen=off_screen,
        window_size=window_size,
    )

    plotter.set_background("white")

    try:
        plotter.enable_anti_aliasing("ssaa")
    except Exception:
        pass

    plotter.add_mesh(
        mesh2d,
        color=mesh_color,
        show_edges=True,
        edge_color=mesh_line_color,
        line_width=mesh_line_width,
    )

    if draw_cylinder:
        cylinder = pv.Cylinder(
            center=(cylinder_center[0], cylinder_center[1], zmid),
            direction=(0.0, 0.0, 1.0),
            radius=cylinder_radius,
            height=0.01,
            resolution=256,
        )

        plotter.add_mesh(
            cylinder,
            color=cylinder_color,
            show_edges=False,
        )

    plotter.add_text(
        mesh_info,
        position="upper_left",
        font_size=13,
        color="black",
        font="courier",
        shadow=True,
    )

    plotter.view_xy()
    plotter.camera.parallel_projection = True

    if xlim is not None and ylim is not None:
        width = xlim[1] - xlim[0]
        height = ylim[1] - ylim[0]
        aspect = window_size[0] / window_size[1]

        plotter.camera.focal_point = (
            0.5 * (xlim[0] + xlim[1]),
            0.5 * (ylim[0] + ylim[1]),
            zmid,
        )

        plotter.camera.parallel_scale = 0.5 * max(
            height,
            width / aspect,
        )

    plotter.show_axes()
    plotter.show(screenshot=output_png, auto_close=True)

    print(f"Saved: {output_png}")


# =================================================
# Main script
# =================================================
if internal_mesh_file is None:
    internal_mesh_file = find_internal_mesh(vtk_dir)

if wall_patch_file is None:
    wall_patch_file = find_wall_patch(vtk_dir)

print(f"Reading internal mesh: {internal_mesh_file}")
print(f"Reading cylinder wall patch: {wall_patch_file}")

mesh = pv.read(internal_mesh_file)
mesh2d, zmid = extract_midplane(mesh)

first_cell_distance = calculate_first_cell_distance(
    mesh2d=mesh2d,
    wall_file=wall_patch_file,
    cylinder_center=cylinder_center,
    zmid=zmid,
)

xmin, xmax, ymin, ymax, _, _ = mesh.bounds

mesh_info = (
    "2D Mesh information\n"
    f"File: {internal_mesh_file.name}\n"
    f"2D cells: {mesh2d.n_cells}\n"
    f"2D points: {mesh2d.n_points}\n"
    f"x range: [{xmin:.2f}, {xmax:.2f}]\n"
    f"y range: [{ymin:.2f}, {ymax:.2f}]\n"
    f"First cell distance y1: {first_cell_distance:.4e}"
)

print(mesh_info)

plot_mesh(
    mesh2d=mesh2d,
    zmid=zmid,
    mesh_info=mesh_info,
    output_png=output_full,
)

plot_mesh(
    mesh2d=mesh2d,
    zmid=zmid,
    mesh_info=mesh_info,
    output_png=output_zoom,
    xlim=zoom_xlim,
    ylim=zoom_ylim,
)
