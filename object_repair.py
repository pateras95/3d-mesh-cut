import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import trimesh
import pymeshfix
import numpy as np
import os

class MeshRepairApp:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # Input and output file paths
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()

        # Input file selection
        ttk.Label(self.parent, text="Input 3D Model File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.parent, textvariable=self.input_file_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(self.parent, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=10, pady=10)

        # Output file selection
        ttk.Label(self.parent, text="Output Repaired Model File:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.parent, textvariable=self.output_file_path, width=50).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self.parent, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=10, pady=10)

        # Repair button
        ttk.Button(self.parent, text="Repair Mesh", command=self.repair_mesh).grid(row=2, column=0, columnspan=3, padx=10, pady=20)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("3D Model Files", "*.obj *.stl *.glb")])
        if file_path:
            self.input_file_path.set(file_path)
            # Set default output file path
            output_path = os.path.splitext(file_path)[0] + "_repaired" + os.path.splitext(file_path)[1]
            self.output_file_path.set(output_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ Files", "*.obj"), ("STL Files", "*.stl"), ("GLB Files", "*.glb")]
        )
        if file_path:
            self.output_file_path.set(file_path)

    def repair_mesh(self):
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input and output files.")
            return

        try:
            # Load the 3D model
            mesh = trimesh.load(input_path)

            # Clean the mesh (remove duplicate vertices, degenerate faces, etc.)
            mesh.process()

            # Check if the mesh is watertight (has no holes)
            if not mesh.is_watertight:
                print("Mesh is not watertight. Filling holes using pymeshfix...")
                # Use pymeshfix to repair the mesh
                mesh = self.repair_with_pymeshfix(mesh)

            # Save the repaired mesh
            mesh.export(output_path)
            messagebox.showinfo("Success", f"Mesh repaired and saved to '{output_path}'.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def repair_with_pymeshfix(self, mesh):
        """
        Use pymeshfix to repair the mesh.
        """
        try:
            # Extract vertices and faces from the mesh
            vertices = mesh.vertices
            faces = mesh.faces

            # Create a pymeshfix mesh object
            meshfix = pymeshfix.MeshFix(vertices, faces)

            # Repair the mesh (fill holes, remove degenerate faces, etc.)
            meshfix.repair()

            # Get the repaired vertices and faces
            repaired_vertices, repaired_faces = meshfix.v, meshfix.f

            # Create a new trimesh object from the repaired data
            repaired_mesh = trimesh.Trimesh(vertices=repaired_vertices, faces=repaired_faces)

            return repaired_mesh

        except Exception as e:
            print(f"Error during pymeshfix repair: {e}")
            return mesh