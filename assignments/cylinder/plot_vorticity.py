import pyvista as pv
import numpy as np
from pathlib import Path

# -------------------------------------------------
# User parameters
# -------------------------------------------------
vtk_file = Path("VTK/cylinder_A1_20000.vtk")

# Set the contour range manually:
# Example: [-0.00135, 0.00135]
# If set to None, the script will use the data range automatically
vort_range = [-2.0, 2.0]

# Mesh line settings
mesh_line_color = "black"
mesh_line_width = 0.5

# -------------------------------------------------
# Read mesh
# -------------------------------------------------
if not vtk_file.exists():
    raise FileNotFoundError(f"Cannot find {vtk_file}")

mesh = pv.read(vtk_file)

print("Reading:", vtk_file)
print("Mesh cells:", mesh.n_cells)
print("Mesh points:", mesh.n_points)
print("Bounds:", mesh.bounds)
print("Available arrays:", mesh.array_names)

# -------------------------------------------------
# Convert cell data to point data for smoother contours
# -------------------------------------------------
mesh = mesh.cell_data_to_point_data()

# -------------------------------------------------
# Extract vorticity
# -------------------------------------------------
if "vorticity" not in mesh.array_names:
    raise KeyError(f"'vorticity' not found. Available arrays: {mesh.array_names}")

vort = mesh["vorticity"]

# For 2D flow, use z-component
if vort.ndim == 2 and vort.shape[1] >= 3:
    omega_z = vort[:, 2]
else:
    omega_z = vort

mesh["omega_z"] = omega_z

# -------------------------------------------------
# Slice at mid-plane if needed
# -------------------------------------------------
zmin, zmax = mesh.bounds[4], mesh.bounds[5]
zmid = 0.5 * (zmin + zmax)

slice2d = mesh.slice(normal="z", origin=(0, 0, zmid))

if slice2d.n_cells == 0:
    print("Slice is empty. Using original mesh.")
    slice2d = mesh

# -------------------------------------------------
# Determine contour range
# -------------------------------------------------
if vort_range is None:
    wmax = np.nanmax(np.abs(slice2d["omega_z"]))
    clim = [-wmax, wmax]
else:
    clim = vort_range

print("Using contour range:", clim)

# -------------------------------------------------
# Plot
# -------------------------------------------------
plotter = pv.Plotter()
plotter.set_background("white")

plotter.add_mesh(
    slice2d,
    scalars="omega_z",
    cmap="coolwarm",
    clim=clim,
    show_edges=True,
    edge_color=mesh_line_color,
    line_width=mesh_line_width,
    scalar_bar_args={"title": "Vorticity"},
)

plotter.view_xy()
plotter.show_axes()
plotter.show()

plotter.screenshot("vorticity_with_mesh.png")
print("Saved: vorticity_with_mesh.png")
