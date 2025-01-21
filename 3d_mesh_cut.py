import vedo
from vedo.applications import FreeHandCutPlotter
from vedo import load
from tkinter import Tk, filedialog

# Hide the main tkinter window
Tk().withdraw()

# Open a file dialog and allow the user to select a 3D file
file_path = filedialog.askopenfilename(
    title="Select a 3D file",
    filetypes=[("3D Files", "*.stl *.obj"), ("STL Files", "*.stl"), ("OBJ Files", "*.obj"), ("All Files", "*.*")]
)

# Check if a file was selected
if not file_path:
    print("No file selected. Exiting.")
else:
    # Set the use of parallel projection to avoid perspective artifacts
    vedo.settings.use_parallel_projection = True

    # Load the mesh from the selected file
    mesh = load(file_path)

    # Initialize the FreeHandCutPlotter with the mesh
    plotter = FreeHandCutPlotter(mesh)

    # Add hover legend to the plotter
    plotter.add_hover_legend()

    # Start the plotter with desired settings
    plotter.start(axes=0, interactive=1).close()