import vedo
from vedo.applications import FreeHandCutPlotter
from vedo import load
from tkinter import Tk, filedialog
import sys 
import os 

root_tk = None 
try:
    if os.name == 'posix' and "DISPLAY" not in os.environ:
        print("3d_mesh_cut.py: No X server (DISPLAY not set).")
    else:
        root_tk = Tk()
        root_tk.withdraw()
except Exception as e:
    print(f"3d_mesh_cut.py: Tkinter init/withdraw failed: {e}")
    pass 

file_path = None
try:
    file_path = filedialog.askopenfilename(
        parent=root_tk, 
        title="Select a 3D file for Vedo Cutter",
        filetypes=[("3D Files", "*.stl *.obj *.ply *.vtk *.vtp"), 
                   ("STL Files", "*.stl"), 
                   ("OBJ Files", "*.obj"), 
                   ("PLY Files", "*.ply"),
                   ("VTK Files", "*.vtk *.vtp"),
                   ("All Files", "*.*")]
    )
except Exception as e_dialog:
    print(f"3d_mesh_cut.py: Error opening filedialog: {e_dialog}")
    if root_tk:
        try: root_tk.destroy()
        except: pass
    sys.exit(1)

if not file_path:
    print("3d_mesh_cut.py: No file selected. Exiting.")
    if root_tk:
        try: root_tk.destroy()
        except: pass
    sys.exit(0)

try:
    print(f"3d_mesh_cut.py: File selected: {file_path}")
    vedo.settings.use_parallel_projection = True
    mesh = load(file_path)

    if not mesh or not mesh.vertices.size:
        print("3d_mesh_cut.py: Loaded mesh is empty or invalid.")
        if root_tk: 
            try: root_tk.destroy()
            except: pass
        sys.exit(1)

    print("3d_mesh_cut.py: Initializing FreeHandCutPlotter...")
    plotter = FreeHandCutPlotter(mesh)
    plotter.add_hover_legend()
    
    print("3d_mesh_cut.py: Starting Vedo plotter...")
    plotter.start(axes=0, interactive=True).close() 
    
    print("3d_mesh_cut.py: Vedo plotter finished.")

except Exception as e:
    print(f"--- Error in 3d_mesh_cut.py ---")
    import traceback
    traceback.print_exc() 
    print(f"-----------------------------")
    if root_tk:
        try: root_tk.destroy()
        except: pass
    sys.exit(1)
finally:
    if root_tk:
        try:
            root_tk.destroy()
        except:
            pass
    # sys.exit(0) # Η έξοδος γίνεται ήδη παραπάνω, δεν χρειάζεται διπλή