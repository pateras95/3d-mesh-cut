import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import trimesh
import pymeshfix
import numpy as np
import os
import traceback
import threading
import queue

# --- Χρωματικό Σχήμα & Γραμματοσειρές (παρόμοια με τον launcher) ---
# Μπορείτε να τα προσαρμόσετε όπως θέλετε
CONTENT_BG = "#f7f9fc"   # Ελαφρώς πιο απαλό λευκό
TEXT_COLOR_PRIMARY = "#2c3e50" # Σκούρο μπλε-γκρι
TEXT_COLOR_SECONDARY = "#7f8c8d" # Πιο ανοιχτό γκρι
ERROR_FG = "#e74c3c"     # Κόκκινο
SUCCESS_FG = "#27ae60"   # Πράσινο
INFO_FG = "#2980b9"      # Μπλε
BUTTON_BG_PRIMARY = "#3498db"
BUTTON_FG_PRIMARY = "white"
BUTTON_HOVER_PRIMARY = "#2980b9"
BUTTON_BG_SECONDARY = "#ecf0f1"
BUTTON_FG_SECONDARY = "#34495e"
BUTTON_HOVER_SECONDARY = "#bdc3c7"
ENTRY_BG = "#ffffff"
ENTRY_FG = "#2c3e50"
BORDER_COLOR = "#dce4ec"

FONT_FAMILY = "Segoe UI" # Ή "Arial", "Helvetica", "Calibri"
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_BUTTON = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_LABEL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_LABEL_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_ENTRY = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_STATUS = (FONT_FAMILY, FONT_SIZE_NORMAL - 1, "italic")


class MeshRepairApp:
    def __init__(self, parent):
        self.parent = parent
        # Ο τίτλος θα ορίζεται από τον launcher αν η εφαρμογή είναι ενσωματωμένη
        # Αυτό είναι χρήσιμο αν τρέχει αυτόνομα.
        toplevel_window = self.parent.winfo_toplevel()
        if hasattr(toplevel_window, 'title') and toplevel_window == self.parent: # Μόνο αν parent είναι το root
            toplevel_window.title("3D Mesh Repair Tool")

        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.status_message = tk.StringVar()
        self.result_queue = queue.Queue()

        self._setup_styles()
        self.create_widgets()
        self.status_message.set("Ready. Select a file to repair.")

    def _setup_styles(self):
        self.style = ttk.Style(self.parent) # Χρήση του parent για το style
        # Προσπάθεια χρήσης ενός θέματος για πιο μοντέρνα εμφάνιση
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            print("Clam theme not available, using default.")

        self.style.configure("App.TFrame", background=CONTENT_BG)

        self.style.configure("App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL)
        self.style.configure("Bold.App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL_BOLD)
        self.style.configure("Status.App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_SECONDARY, font=FONT_STATUS)
        self.style.configure("Error.App.TLabel", background=CONTENT_BG, foreground=ERROR_FG, font=FONT_STATUS)
        self.style.configure("Success.App.TLabel", background=CONTENT_BG, foreground=SUCCESS_FG, font=FONT_STATUS)


        self.style.configure("App.TEntry",
                             fieldbackground=ENTRY_BG,
                             foreground=ENTRY_FG,
                             font=FONT_ENTRY,
                             borderwidth=1,
                             relief=tk.FLAT,
                             padding=5)
        self.style.map("App.TEntry",
                       bordercolor=[('focus', INFO_FG), ('!focus', BORDER_COLOR)],
                       relief=[('focus', tk.SOLID), ('!focus', tk.SOLID)])


        self.style.configure("Primary.TButton",
                             font=FONT_BUTTON,
                             background=BUTTON_BG_PRIMARY,
                             foreground=BUTTON_FG_PRIMARY,
                             padding=(10, 8),
                             borderwidth=0,
                             relief=tk.FLAT)
        self.style.map("Primary.TButton",
                       background=[('active', BUTTON_HOVER_PRIMARY), ('pressed', BUTTON_HOVER_PRIMARY), ('disabled', '#cccccc')],
                       foreground=[('disabled', '#666666')])

        self.style.configure("Secondary.TButton",
                             font=FONT_BUTTON,
                             background=BUTTON_BG_SECONDARY,
                             foreground=BUTTON_FG_SECONDARY,
                             padding=(8, 6),
                             borderwidth=1,
                             relief=tk.FLAT)
        self.style.map("Secondary.TButton",
                       background=[('active', BUTTON_HOVER_SECONDARY), ('pressed', BUTTON_HOVER_SECONDARY)],
                       bordercolor=[('active', INFO_FG), ('!active', BORDER_COLOR)],
                       relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])
        
        self.style.configure("Repair.Horizontal.TProgressbar", troughcolor=BUTTON_BG_SECONDARY, background=BUTTON_BG_PRIMARY)


    def create_widgets(self):
        # Χρησιμοποιούμε το self.parent απευθείας για τοποθέτηση,
        # καθώς αυτό είναι το frame που μας δίνεται από τον launcher.
        self.parent.columnconfigure(0, weight=1) # Για να επεκτείνεται το main_frame
        self.parent.rowconfigure(0, weight=1)    # Για να επεκτείνεται το main_frame

        main_frame = ttk.Frame(self.parent, padding="15 20", style="App.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Input File Section ---
        input_group = ttk.Frame(main_frame, style="App.TFrame")
        input_group.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,10))
        input_group.columnconfigure(1, weight=1)

        ttk.Label(input_group, text="Input 3D Model:", style="Bold.App.TLabel").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.input_entry = ttk.Entry(input_group, textvariable=self.input_file_path, width=60, style="App.TEntry")
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_input_button = ttk.Button(input_group, text="Browse", command=self.browse_input_file, style="Secondary.TButton")
        self.browse_input_button.grid(row=0, column=2, padx=(5,0), pady=5)

        # --- Output File Section ---
        output_group = ttk.Frame(main_frame, style="App.TFrame")
        output_group.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,20))
        output_group.columnconfigure(1, weight=1)

        ttk.Label(output_group, text="Output Repaired Model:", style="Bold.App.TLabel").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.output_entry = ttk.Entry(output_group, textvariable=self.output_file_path, width=60, style="App.TEntry")
        self.output_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_output_button = ttk.Button(output_group, text="Browse", command=self.browse_output_file, style="Secondary.TButton")
        self.browse_output_button.grid(row=0, column=2, padx=(5,0), pady=5)

        # --- Action Button ---
        self.repair_button = ttk.Button(main_frame, text="Repair Mesh", command=self.start_repair_mesh_thread, style="Primary.TButton")
        self.repair_button.grid(row=2, column=0, columnspan=3, padx=5, pady=(10,5), sticky="ew")

        # --- Status Bar ---
        status_frame = ttk.Frame(main_frame, style="App.TFrame", padding=(0,10,0,0))
        status_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(status_frame, textvariable=self.status_message, style="Status.App.TLabel", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(5,0))

        self.progress_bar = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='indeterminate', style="Repair.Horizontal.TProgressbar")
        self.progress_bar.grid(row=1, column=0, columnspan=1, sticky="ew", pady=(5,0), padx=5)

        main_frame.columnconfigure(1, weight=1) # Για τα entry fields

        # Εξασφάλιση ότι το main_frame επεκτείνεται μέσα στο self.parent
        # Αυτό είναι σημαντικό όταν το self.parent είναι το frame από τον launcher
        for i in range(4): # Αριθμός σειρών στο main_frame
            main_frame.rowconfigure(i, weight=0) # Αρχικά, μην δίνεις βάρος στις σειρές
        main_frame.rowconfigure(3, weight=1) # Δώσε βάρος στη σειρά του status bar για να πάει κάτω

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input 3D Model",
            filetypes=[
                ("3D Model Files", "*.obj *.stl *.ply *.glb *.gltf"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_repaired{ext}"
            self.output_file_path.set(output_path)
            self.status_message.set(f"Input: {os.path.basename(file_path)}. Ready to repair.")
            self.status_label.config(style="Status.App.TLabel") # Επαναφορά στυλ

    def browse_output_file(self):
        input_ext = os.path.splitext(self.input_file_path.get())[1]
        if not input_ext: input_ext = ".obj"
        file_path = filedialog.asksaveasfilename(
            title="Save Repaired Model As",
            defaultextension=input_ext,
            filetypes=[
                ("OBJ Files", "*.obj"), ("STL Files", "*.stl"),
                ("PLY Files", "*.ply"), ("GLB Files", "*.glb"),
                ("GLTF Files", "*.gltf"), ("All Files", "*.*")
            ]
        )
        if file_path:
            self.output_file_path.set(file_path)
            self.status_message.set("Output path selected. Ready to repair.")
            self.status_label.config(style="Status.App.TLabel")

    def start_repair_mesh_thread(self):
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input and output files.")
            return

        self.repair_button.config(state=tk.DISABLED)
        self.browse_input_button.config(state=tk.DISABLED)
        self.browse_output_button.config(state=tk.DISABLED)
        self.input_entry.config(state=tk.DISABLED)
        self.output_entry.config(state=tk.DISABLED)

        self.status_message.set("Starting repair process...")
        self.status_label.config(style="Status.App.TLabel")
        self.progress_bar.start(10) # Το 10 είναι το interval σε ms

        # Δημιουργία και εκκίνηση του thread
        thread = threading.Thread(target=self._perform_repair_task,
                                  args=(input_path, output_path),
                                  daemon=True) # Daemon thread για να κλείνει με την εφαρμογή
        thread.start()

        # Έναρξη ελέγχου της ουράς αποτελεσμάτων
        self.parent.after(100, self._check_repair_queue)

    def _update_status(self, message, style="Status.App.TLabel"):
        """Βοηθητική συνάρτηση για ενημέρωση του status label από το κύριο thread."""
        self.status_message.set(message)
        self.status_label.config(style=style)
        self.parent.update_idletasks() # Άμεση ενημέρωση του GUI


    def _perform_repair_task(self, input_path, output_path):
        """Αυτή η συνάρτηση εκτελείται στο ξεχωριστό thread."""
        try:
            self.result_queue.put(("progress", f"Loading mesh: {os.path.basename(input_path)}"))
            loaded_object = trimesh.load(input_path, process=False, force='mesh')

            if isinstance(loaded_object, trimesh.Scene):
                self.result_queue.put(("progress", "Input is a scene. Concatenating geometries..."))
                mesh_list = [m for m in loaded_object.geometry.values() if isinstance(m, trimesh.Trimesh)]
                if not mesh_list:
                    self.result_queue.put(("error", "The scene contains no valid mesh geometry."))
                    return
                mesh = trimesh.util.concatenate(mesh_list) if len(mesh_list) > 1 else mesh_list[0]
            elif isinstance(loaded_object, trimesh.Trimesh):
                mesh = loaded_object
            else:
                self.result_queue.put(("error", f"Unsupported mesh type: {type(loaded_object)}"))
                return

            if not mesh.vertices.size or not mesh.faces.size:
                self.result_queue.put(("error", "Loaded mesh has no vertices or faces."))
                return

            self.result_queue.put(("progress", "Initial processing..."))
            mesh.process()

            if mesh.body_count > 1:
                self.result_queue.put(("progress", f"Mesh has {mesh.body_count} bodies. Selecting largest..."))
                # ... (η λογική για επιλογή του μεγαλύτερου component παραμένει ίδια) ...
                components = mesh.split()
                valid_components = []
                for comp in components:
                    if hasattr(comp, 'volume') and comp.volume is not None and comp.faces.shape[0] > 0:
                        if comp.volume == 0 and comp.is_watertight:
                             valid_components.append({'component': comp, 'metric': len(comp.faces)})
                        elif comp.volume > 0:
                             valid_components.append({'component': comp, 'metric': comp.volume})
                if not valid_components and components:
                    valid_components = [{'component': comp, 'metric': len(comp.faces)} for comp in components if comp.faces.shape[0] > 0]
                if valid_components:
                    valid_components.sort(key=lambda x: x['metric'], reverse=True)
                    mesh = valid_components[0]['component']
                    mesh.process()
                else:
                    self.result_queue.put(("progress", "Could not determine largest component. Proceeding..."))


            self.result_queue.put(("progress", "Fixing normals and winding order..."))
            trimesh.repair.fix_normals(mesh)
            trimesh.repair.fix_winding(mesh)
            mesh.process()

            if not mesh.is_watertight:
                self.result_queue.put(("progress", "Attempting trimesh.fill_holes()..."))
                trimesh.repair.fill_holes(mesh)
                mesh.process()
                if mesh.is_watertight:
                    self.result_queue.put(("progress", "Watertight after trimesh.fill_holes()."))


            if not mesh.is_watertight:
                self.result_queue.put(("progress", "Attempting repair with pymeshfix..."))
                try:
                    meshfix = pymeshfix.MeshFix(mesh.vertices, mesh.faces)
                    meshfix.repair(verbose=False, joincomp=True, remove_smallest_components=True)
                    repaired_v, repaired_f = meshfix.v, meshfix.f
                    if repaired_v.size > 0 and repaired_f.size > 0:
                        repaired_mesh_pymeshfix = trimesh.Trimesh(vertices=repaired_v, faces=repaired_f)
                        repaired_mesh_pymeshfix.process()
                        if repaired_mesh_pymeshfix.is_watertight or \
                           (not mesh.is_watertight and len(repaired_mesh_pymeshfix.faces) >= len(mesh.faces)):
                            mesh = repaired_mesh_pymeshfix
                            self.result_queue.put(("progress", "Applied pymeshfix result."))
                            if mesh.is_watertight:
                                self.result_queue.put(("progress", "Watertight after pymeshfix."))

                        else:
                             self.result_queue.put(("progress", "pymeshfix did not improve. Keeping previous."))
                    else:
                        self.result_queue.put(("progress", "pymeshfix produced empty mesh. Discarding."))
                except Exception as e_pymeshfix:
                    self.result_queue.put(("progress", f"pymeshfix error: {e_pymeshfix}. Continuing..."))
            
            if not mesh.is_watertight:
                self.result_queue.put(("progress", "Final attempt with trimesh.fill_holes()..."))
                trimesh.repair.fill_holes(mesh)
                mesh.process()
                if mesh.is_watertight:
                    self.result_queue.put(("progress", "Watertight after final trimesh.fill_holes()."))


            self.result_queue.put(("progress", "Final check and exporting..."))
            if not mesh.vertices.size or not mesh.faces.size:
                 self.result_queue.put(("error", "Processing resulted in an empty mesh. Cannot save."))
                 return

            mesh.export(output_path)
            final_watertight_status = mesh.is_watertight
            
            if final_watertight_status:
                self.result_queue.put(("success", f"Mesh successfully repaired and saved to '{os.path.basename(output_path)}'. Watertight: YES"))
            else:
                self.result_queue.put(("warning", f"Mesh repaired and saved to '{os.path.basename(output_path)}'. Watertight: NO"))

        except Exception as e:
            detailed_error = traceback.format_exc()
            # Log the full error to console for debugging, send a simpler one to UI
            print(f"Full error traceback in thread:\n{detailed_error}")
            self.result_queue.put(("error", f"Repair failed: {e}"))


    def _check_repair_queue(self):
        try:
            message_type, message_content = self.result_queue.get_nowait()

            if message_type == "progress":
                self._update_status(message_content)
                self.parent.after(100, self._check_repair_queue) # Συνέχεια ελέγχου
            elif message_type == "success":
                self._finalize_repair_ui()
                self._update_status(message_content, "Success.App.TLabel")
                messagebox.showinfo("Success", message_content)
            elif message_type == "warning":
                self._finalize_repair_ui()
                self._update_status(message_content, "Error.App.TLabel") # Χρησιμοποιούμε error style για warning στο status
                messagebox.showwarning("Warning", message_content)
            elif message_type == "error":
                self._finalize_repair_ui()
                self._update_status(message_content, "Error.App.TLabel")
                messagebox.showerror("Error", message_content)
            
        except queue.Empty:
            # Αν η ουρά είναι άδεια, συνέχισε τον έλεγχο αργότερα
            self.parent.after(100, self._check_repair_queue)
        except Exception as e:
            # Απρόοπτο σφάλμα κατά τον έλεγχο της ουράς
            self._finalize_repair_ui()
            tb_str = traceback.format_exc()
            self._update_status(f"Queue check error: {e}", "Error.App.TLabel")
            print(f"Error checking queue: {e}\n{tb_str}")
            messagebox.showerror("Internal Error", f"An error occurred while processing results: {e}")


    def _finalize_repair_ui(self):
        """Επαναφέρει το UI στην κανονική του κατάσταση μετά την ολοκλήρωση/σφάλμα."""
        self.repair_button.config(state=tk.NORMAL)
        self.browse_input_button.config(state=tk.NORMAL)
        self.browse_output_button.config(state=tk.NORMAL)
        self.input_entry.config(state=tk.NORMAL)
        self.output_entry.config(state=tk.NORMAL)
        self.progress_bar.stop()


# --- Για αυτόνομη εκτέλεση ---
def main():
    root = tk.Tk()
    # Δεν χρειάζεται να ορίσουμε τίτλο εδώ, η κλάση το χειρίζεται
    # root.geometry("700x350") # Ένα λογικό μέγεθος για αυτόνομη εκτέλεση

    # Δημιουργούμε ένα κύριο frame που θα γεμίσει το root window,
    # και το περνάμε ως parent στην MeshRepairApp.
    # Αυτό προσομοιώνει καλύτερα τη δομή του launcher.
    app_container = ttk.Frame(root, style="App.TFrame")
    app_container.pack(fill=tk.BOTH, expand=True)

    app = MeshRepairApp(app_container) # Περνάμε το container ως parent
    root.mainloop()

if __name__ == '__main__':
    main()