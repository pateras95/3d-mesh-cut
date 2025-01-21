import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from PIL import Image  # For WebP texture conversion

class GLBOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GLB/GLTF Optimizer - glTF-Transform v4 + WebP")

        # Input and output file paths
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()

        # Compression settings
        self.draco_compression = tk.BooleanVar(value=True)
        self.texture_compression = tk.BooleanVar(value=True)
        self.texture_resolution = tk.IntVar(value=1024)  # Max texture resolution
        self.webp_quality = tk.IntVar(value=80)  # WebP quality (0-100)

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Input file selection
        tk.Label(self.root, text="Input GLB/GLTF File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.input_file_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=10, pady=10)

        # Output file selection
        tk.Label(self.root, text="Output GLB/GLTF File:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.output_file_path, width=50).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=10, pady=10)

        # Draco compression settings
        tk.Checkbutton(self.root, text="Enable Draco Compression", variable=self.draco_compression).grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        # Texture compression settings
        tk.Checkbutton(self.root, text="Enable Texture Compression", variable=self.texture_compression).grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        tk.Label(self.root, text="Max Texture Resolution:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        tk.Scale(self.root, from_=256, to=4096, orient="horizontal", variable=self.texture_resolution).grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        tk.Label(self.root, text="WebP Quality (0-100):").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        tk.Scale(self.root, from_=0, to=100, orient="horizontal", variable=self.webp_quality).grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Optimize button
        tk.Button(self.root, text="Optimize", command=self.optimize_file).grid(row=6, column=0, columnspan=3, padx=10, pady=20)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("GLB/GLTF Files", "*.glb *.gltf")])
        if file_path:
            self.input_file_path.set(file_path)
            # Set default output file path
            output_path = os.path.splitext(file_path)[0] + "_optimized.glb"
            self.output_file_path.set(output_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".glb", filetypes=[("GLB Files", "*.glb"), ("GLTF Files", "*.gltf")])
        if file_path:
            self.output_file_path.set(file_path)

    def resize_texture(self, image_path, max_resolution):
        """
        Resize a texture to the specified maximum resolution.
        """
        with Image.open(image_path) as img:
            width, height = img.size
            if width > max_resolution or height > max_resolution:
                img.thumbnail((max_resolution, max_resolution), Image.ANTIALIAS)
                img.save(image_path)
                print(f"Resized {image_path} to {img.size}")

    def convert_textures_to_webp(self, gltf_folder):
        """
        Convert all textures in the GLTF folder to WebP format.
        """
        for root, _, files in os.walk(gltf_folder):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_path = os.path.join(root, file)
                    webp_path = os.path.splitext(image_path)[0] + ".webp"
                    try:
                        # Resize texture if necessary
                        self.resize_texture(image_path, self.texture_resolution.get())
                        # Convert to WebP
                        with Image.open(image_path) as img:
                            img.save(webp_path, "WEBP", quality=self.webp_quality.get())
                        os.remove(image_path)  # Delete the original texture
                        print(f"Converted {image_path} to WebP: {webp_path}")
                    except Exception as e:
                        print(f"Failed to convert {image_path} to WebP: {e}")

    def optimize_with_gltf_transform(self, input_path, output_path):
        """
        Optimize the GLB/GLTF file using glTF-Transform v4.
        """
        try:
            # Temporary file for intermediate steps
            temp_path = os.path.splitext(output_path)[0] + "_temp.glb"

            # Step 1: Resize textures (if enabled)
            if self.texture_compression.get():
                resize_command = [
                    "gltf-transform", "resize",
                    input_path, temp_path,
                    "--width", str(self.texture_resolution.get()),
                    "--height", str(self.texture_resolution.get())
                ]
                result = subprocess.run(resize_command, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error during texture resizing: {result.stderr}")
                else:
                    input_path = temp_path  # Use the resized file for the next step

            # Step 2: Compress textures (if enabled)
            if self.texture_compression.get():
                texture_compress_command = [
                    "gltf-transform", "texture-compress",
                    input_path, temp_path,
                    "--format", "webp",
                    "--quality", str(self.webp_quality.get())
                ]
                result = subprocess.run(texture_compress_command, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error during texture compression: {result.stderr}")
                else:
                    input_path = temp_path  # Use the compressed file for the next step

            # Step 3: Apply Draco compression (if enabled)
            if self.draco_compression.get():
                draco_command = [
                    "gltf-transform", "draco",
                    input_path, output_path
                ]
                result = subprocess.run(draco_command, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error during Draco compression: {result.stderr}")
            else:
                # If Draco compression is not enabled, copy the file to the output path
                import shutil
                shutil.copyfile(input_path, output_path)

            # Clean up temporary files
            if os.path.exists(temp_path):
                os.remove(temp_path)

            print(f"Optimization successful. Output saved to '{output_path}'.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def optimize_file(self):
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input and output files.")
            return

        try:
            # If the input is a GLTF file, extract the folder path
            if input_path.lower().endswith(".gltf"):
                gltf_folder = os.path.dirname(input_path)
                # Convert textures to WebP if enabled
                if self.texture_compression.get():
                    self.convert_textures_to_webp(gltf_folder)

            # Optimize using glTF-Transform
            self.optimize_with_gltf_transform(input_path, output_path)
            messagebox.showinfo("Success", f"Optimization successful. Output saved to '{output_path}'.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GLBOptimizerApp(root)
    root.mainloop()