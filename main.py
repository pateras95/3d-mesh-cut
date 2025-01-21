import tkinter as tk
from tkinter import ttk

# Function to clear the big block and embed the script's UI
def run_script(script_name):
    # Clear the big block
    for widget in big_block.winfo_children():
        widget.destroy()

    # Dynamically import the script
    try:
        script_module = __import__(script_name)
        
        # Create a frame in the big block for the script's UI
        script_frame = ttk.Frame(big_block)
        script_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Run the script's GUI inside the frame
        if script_name == "object_repair":
            script_module.MeshRepairApp(script_frame)
        elif script_name == "gltf_optimizer":
            script_module.GLBOptimizerApp(script_frame)

    except Exception as e:
        # Display an error message if the script fails to load
        error_label = ttk.Label(big_block, text=f"Error loading {script_name}: {e}", foreground="red")
        error_label.pack(pady=20)

# Create the main window
root = tk.Tk()
root.title("Script Launcher")
root.geometry("1200x800")
root.configure(bg="#f0f0f0")

# Create a sidebar (burger menu)
sidebar = tk.Frame(root, bg="#333333", width=200)
sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Add buttons to the sidebar
button_style = ttk.Style()
button_style.configure("TButton", font=("Arial", 12), padding=10)

button1 = ttk.Button(
    sidebar,
    text="Object Repair",
    command=lambda: run_script("object_repair")
)
button1.pack(pady=10, padx=10, fill=tk.X)

button2 = ttk.Button(
    sidebar,
    text="GLTF Optimizer",
    command=lambda: run_script("gltf_optimizer")
)
button2.pack(pady=10, padx=10, fill=tk.X)

button3 = ttk.Button(
    sidebar,
    text="3D Mesh Cut",
    command=lambda: run_script("3d_mesh_cut")
)
button3.pack(pady=10, padx=10, fill=tk.X)

# Create the big block (top) for script windows
big_block = tk.Frame(root, bg="#ffffff", relief=tk.SUNKEN, borderwidth=2)
big_block.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()