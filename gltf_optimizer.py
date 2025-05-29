import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import queue
import traceback
import shutil
import re

# --- Σταθερές Χρωμάτων & Γραμματοσειρών ---
CONTENT_BG = "#f7f9fc"
TEXT_COLOR_PRIMARY = "#2c3e50"
TEXT_COLOR_SECONDARY = "#7f8c8d"
ERROR_FG = "#e74c3c"
SUCCESS_FG = "#27ae60"
INFO_FG = "#2980b9"
BUTTON_BG_PRIMARY = "#3498db"
BUTTON_FG_PRIMARY = "white"
BUTTON_HOVER_PRIMARY = "#2980b9"
BUTTON_BG_SECONDARY = "#ecf0f1"
BUTTON_FG_SECONDARY = "#34495e"
BUTTON_HOVER_SECONDARY = "#bdc3c7"
ENTRY_BG = "#ffffff"
ENTRY_FG = "#2c3e50"
BORDER_COLOR = "#dce4ec"
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_INFO = 9
FONT_SIZE_INSPECT = 8 
FONT_BUTTON = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_LABEL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_LABEL_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_ENTRY = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_STATUS = (FONT_FAMILY, FONT_SIZE_NORMAL -1, "italic")
FONT_SECTION_TITLE = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold", "underline")
FONT_INFO_LABEL = (FONT_FAMILY, FONT_SIZE_INFO)
FONT_INFO_VALUE = (FONT_FAMILY, FONT_SIZE_INFO, "bold")

GLTF_TRANSFORM_CLI = "gltf-transform"

class GLBOptimizerApp:
    def __init__(self, parent):
        self.parent = parent
        toplevel_window = self.parent.winfo_toplevel()
        if hasattr(toplevel_window, 'title') and toplevel_window == self.parent:
            toplevel_window.title("GLB/GLTF Optimizer (Display Inspect)")

        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        
        self.use_draco = tk.BooleanVar(value=True)
        self.process_textures = tk.BooleanVar(value=True)
        self.webp_quality = tk.IntVar(value=75)

        self.info_before_size = tk.StringVar(value="N/A")
        self.info_after_size = tk.StringVar(value="N/A")

        self.status_message = tk.StringVar()
        self.result_queue = queue.Queue()

        self._setup_styles()
        self.create_widgets()
        self.status_message.set("Ready. Select a file to optimize.")

    def _setup_styles(self):
        self.style = ttk.Style(self.parent)
        try: self.style.theme_use('clam')
        except tk.TclError: print("Clam theme not available, using default.")
        self.style.configure("App.TFrame", background=CONTENT_BG)
        self.style.configure("App.TLabelframe", background=CONTENT_BG, bordercolor=BORDER_COLOR) # Για το Labelframe
        self.style.configure("App.TLabelframe.Label", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL_BOLD) # Για τον τίτλο του Labelframe

        self.style.configure("App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL)
        self.style.configure("Bold.App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL_BOLD)
        self.style.configure("Section.App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_SECTION_TITLE)
        self.style.configure("Status.App.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_SECONDARY, font=FONT_STATUS)
        self.style.configure("Error.App.TLabel", background=CONTENT_BG, foreground=ERROR_FG, font=FONT_STATUS)
        self.style.configure("Success.App.TLabel", background=CONTENT_BG, foreground=SUCCESS_FG, font=FONT_STATUS)
        self.style.configure("App.TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG, font=FONT_ENTRY, borderwidth=1, relief=tk.FLAT, padding=5)
        self.style.map("App.TEntry", bordercolor=[('focus', INFO_FG), ('!focus', BORDER_COLOR)], relief=[('focus', tk.SOLID), ('!focus', tk.SOLID)])
        self.style.configure("Primary.TButton", font=FONT_BUTTON, background=BUTTON_BG_PRIMARY, foreground=BUTTON_FG_PRIMARY, padding=(10, 8), borderwidth=0, relief=tk.FLAT)
        self.style.map("Primary.TButton", background=[('active', BUTTON_HOVER_PRIMARY), ('pressed', BUTTON_HOVER_PRIMARY), ('disabled', '#cccccc')], foreground=[('disabled', '#666666')])
        self.style.configure("Secondary.TButton", font=FONT_BUTTON, background=BUTTON_BG_SECONDARY, foreground=BUTTON_FG_SECONDARY, padding=(8, 6), borderwidth=1, relief=tk.FLAT)
        self.style.map("Secondary.TButton", background=[('active', BUTTON_HOVER_SECONDARY), ('pressed', BUTTON_HOVER_SECONDARY)], bordercolor=[('active', INFO_FG), ('!active', BORDER_COLOR)], relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])
        self.style.configure("App.TCheckbutton", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_LABEL)
        self.style.map("App.TCheckbutton", indicatorcolor=[('selected', BUTTON_BG_PRIMARY), ('!selected', BORDER_COLOR)])
        self.style.configure("Optimize.Horizontal.TProgressbar", troughcolor=BUTTON_BG_SECONDARY, background=BUTTON_BG_PRIMARY)
        self.style.configure("Info.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_SECONDARY, font=FONT_INFO_LABEL)
        self.style.configure("InfoValue.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR_PRIMARY, font=FONT_INFO_VALUE)

    def create_widgets(self):
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=3) 
        self.parent.rowconfigure(1, weight=2) # Αύξηση βάρους για το inspect output

        main_content_frame = ttk.Frame(self.parent, style="App.TFrame")
        main_content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,0))
        
        main_frame = ttk.Frame(main_content_frame, padding="15 20", style="App.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        row_idx = 0
        ttk.Label(main_frame, text="File Selection", style="Section.App.TLabel").grid(row=row_idx, column=0, columnspan=3, sticky="w", pady=(0, 5)); row_idx += 1
        ttk.Label(main_frame, text="Input GLB/GLTF:", style="Bold.App.TLabel").grid(row=row_idx, column=0, padx=(0,10), pady=2, sticky="w")
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_file_path, width=50, style="App.TEntry")
        self.input_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.browse_input_button = ttk.Button(main_frame, text="Browse", command=self.browse_input_file, style="Secondary.TButton")
        self.browse_input_button.grid(row=row_idx, column=2, padx=(5,0), pady=2); row_idx += 1
        ttk.Label(main_frame, text="Output GLB File:", style="Bold.App.TLabel").grid(row=row_idx, column=0, padx=(0,10), pady=2, sticky="w")
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_file_path, width=50, style="App.TEntry")
        self.output_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        self.browse_output_button = ttk.Button(main_frame, text="Browse", command=self.browse_output_file, style="Secondary.TButton")
        self.browse_output_button.grid(row=row_idx, column=2, padx=(5,0), pady=2); row_idx += 1

        info_frame = ttk.Frame(main_frame, style="App.TFrame", padding=(0, 5, 0, 5))
        info_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", pady=(5,0)); row_idx += 1
        ttk.Label(info_frame, text="Original Size:", style="Info.TLabel").grid(row=0, column=0, sticky="w", padx=(5,5))
        ttk.Label(info_frame, textvariable=self.info_before_size, style="InfoValue.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(info_frame, text="Optimized Size:", style="Info.TLabel").grid(row=0, column=2, sticky="w", padx=(25,5))
        ttk.Label(info_frame, textvariable=self.info_after_size, style="InfoValue.TLabel").grid(row=0, column=3, sticky="w")
        info_frame.columnconfigure(1, weight=1) 
        info_frame.columnconfigure(3, weight=1)

        ttk.Separator(main_frame, orient='horizontal').grid(row=row_idx, column=0, columnspan=3, sticky='ew', pady=10); row_idx += 1
        
        ttk.Label(main_frame, text="Optimization Settings", style="Section.App.TLabel").grid(row=row_idx, column=0, columnspan=3, sticky="w", pady=(0,5)); row_idx += 1
        self.draco_cb = ttk.Checkbutton(main_frame, text="Enable Draco Compression (geometry)", variable=self.use_draco, style="App.TCheckbutton")
        self.draco_cb.grid(row=row_idx, column=0, columnspan=3, padx=0, pady=2, sticky="w"); row_idx += 1
        self.texture_cb = ttk.Checkbutton(main_frame, text="Process Textures (Compress with gltf-transform webp)", variable=self.process_textures, command=self._toggle_texture_options, style="App.TCheckbutton")
        self.texture_cb.grid(row=row_idx, column=0, columnspan=3, padx=0, pady=2, sticky="w"); row_idx += 1
        self.texture_options_frame = ttk.Frame(main_frame, style="App.TFrame")
        self.texture_options_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", padx=(20, 0)); row_idx += 1
        self.texture_options_frame.columnconfigure(1, weight=1)
        ttk.Label(self.texture_options_frame, text="WebP Quality (gltf-transform):", style="App.TLabel").grid(row=0, column=0, padx=(0,10), pady=2, sticky="w")
        self.webp_q_val_label = ttk.Label(self.texture_options_frame, text=str(self.webp_quality.get()), style="Bold.App.TLabel", width=5, anchor="e")
        self.webp_q_val_label.grid(row=0, column=2, padx=(5,0), pady=2, sticky="w")
        self.webp_q_scale = ttk.Scale(self.texture_options_frame, from_=1, to=100, orient="horizontal", variable=self.webp_quality, command=lambda v: self.webp_q_val_label.config(text=str(int(float(v)))))
        self.webp_q_scale.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self._toggle_texture_options()

        ttk.Separator(main_frame, orient='horizontal').grid(row=row_idx, column=0, columnspan=3, sticky='ew', pady=10); row_idx += 1
        self.optimize_button = ttk.Button(main_frame, text="Optimize", command=self.start_optimize_thread, style="Primary.TButton")
        self.optimize_button.grid(row=row_idx, column=0, columnspan=3, padx=5, pady=(5,2), sticky="ew"); row_idx += 1
        
        status_frame = ttk.Frame(main_frame, style="App.TFrame", padding=(0,5,0,0))
        status_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew"); row_idx += 1
        status_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_message, style="Status.App.TLabel", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=(5,0))
        self.progress_bar = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='indeterminate', style="Optimize.Horizontal.TProgressbar")
        self.progress_bar.grid(row=1, column=0, columnspan=1, sticky="ew", pady=(2,0), padx=5)

        # --- Frame για την έξοδο του Inspect ---
        inspect_output_frame = ttk.Labelframe(self.parent, text="gltf-transform inspect Details", style="App.TLabelframe", padding="5")
        inspect_output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10)) # Αλλαγή pady
        inspect_output_frame.columnconfigure(0, weight=1) # Για το Before Text
        inspect_output_frame.columnconfigure(1, weight=0) # Για το Before Y Scroll
        inspect_output_frame.columnconfigure(2, weight=1) # Για το After Text
        inspect_output_frame.columnconfigure(3, weight=0) # Για το After Y Scroll
        inspect_output_frame.rowconfigure(0, weight=1)    # Για τα Text widgets
        inspect_output_frame.rowconfigure(1, weight=0)    # Για τα X Scrollbars

        # Before Inspect Output
        ttk.Label(inspect_output_frame, text="Original Model Details:", style="Bold.App.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,2))
        self.inspect_text_before = tk.Text(inspect_output_frame, wrap=tk.NONE, height=6, width=40, font=(FONT_FAMILY, FONT_SIZE_INSPECT), relief=tk.SOLID, borderwidth=1, background=ENTRY_BG, foreground=ENTRY_FG)
        self.inspect_text_before.grid(row=1, column=0, sticky="nsew", pady=2)
        inspect_scroll_y_before = ttk.Scrollbar(inspect_output_frame, orient=tk.VERTICAL, command=self.inspect_text_before.yview)
        inspect_scroll_y_before.grid(row=1, column=1, sticky="ns", pady=2)
        inspect_scroll_x_before = ttk.Scrollbar(inspect_output_frame, orient=tk.HORIZONTAL, command=self.inspect_text_before.xview)
        inspect_scroll_x_before.grid(row=2, column=0, sticky="ew")
        self.inspect_text_before.config(yscrollcommand=inspect_scroll_y_before.set, xscrollcommand=inspect_scroll_x_before.set, state=tk.DISABLED)

        # After Inspect Output
        ttk.Label(inspect_output_frame, text="Optimized Model Details:", style="Bold.App.TLabel").grid(row=0, column=2, columnspan=2, sticky="w", pady=(0,2), padx=(10,0))
        self.inspect_text_after = tk.Text(inspect_output_frame, wrap=tk.NONE, height=6, width=40, font=(FONT_FAMILY, FONT_SIZE_INSPECT), relief=tk.SOLID, borderwidth=1, background=ENTRY_BG, foreground=ENTRY_FG)
        self.inspect_text_after.grid(row=1, column=2, sticky="nsew", padx=(10,0), pady=2)
        inspect_scroll_y_after = ttk.Scrollbar(inspect_output_frame, orient=tk.VERTICAL, command=self.inspect_text_after.yview)
        inspect_scroll_y_after.grid(row=1, column=3, sticky="ns", padx=(0,0), pady=2) # Αφαίρεση padx
        inspect_scroll_x_after = ttk.Scrollbar(inspect_output_frame, orient=tk.HORIZONTAL, command=self.inspect_text_after.xview)
        inspect_scroll_x_after.grid(row=2, column=2, sticky="ew", padx=(10,0))
        self.inspect_text_after.config(yscrollcommand=inspect_scroll_y_after.set, xscrollcommand=inspect_scroll_x_after.set, state=tk.DISABLED)

    def _toggle_texture_options(self):
        state = tk.NORMAL if self.process_textures.get() else tk.DISABLED
        for child in self.texture_options_frame.winfo_children():
            try: child.config(state=state)
            except tk.TclError:
                if isinstance(child, ttk.Scale): child.state(["!disabled" if state == tk.NORMAL else "disabled"])

    def _get_file_size_formatted(self, file_path):
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024: return f"{size_bytes} B"
            elif size_bytes < 1024**2: return f"{size_bytes/1024:.2f} KB"
            elif size_bytes < 1024**3: return f"{size_bytes/(1024**2):.2f} MB"
            else: return f"{size_bytes/(1024**3):.2f} GB"
        except FileNotFoundError: return "N/A"
        except Exception: return "Error"

    def _get_inspect_output(self, file_path): # Τροποποιημένη μέθοδος
        if not os.path.exists(file_path):
            return "File not found."
        try:
            cmd_inspect = [GLTF_TRANSFORM_CLI, "inspect", file_path]
            
            # Προσπάθεια απενεργοποίησης χρωμάτων από το gltf-transform (αν υποστηρίζεται)
            # Οι μεταβλητές περιβάλλοντος είναι ένας συνήθης τρόπος
            env = os.environ.copy()
            env["NO_COLOR"] = "1" # Πολλά CLI εργαλεία σέβονται αυτό
            env["TERM"] = "dumb"  # Άλλος τρόπος για να υποδηλώσει non-color terminal

            result = subprocess.run(cmd_inspect, 
                                    capture_output=True, 
                                    text=True, 
                                    check=False, 
                                    encoding='utf-8',
                                    env=env) # Πέρασμα του τροποποιημένου περιβάλλοντος

            if result.returncode == 0:
                output_str = result.stdout.strip() if result.stdout else "Inspect returned no output."
                
                # Αφαίρεση ANSI escape codes
                # Το regex ψάχνει για το μοτίβο ESC[...m
                ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                cleaned_output = ansi_escape_pattern.sub('', output_str)
                
                return cleaned_output
            else:
                error_output = result.stderr or result.stdout or 'No error message.'
                ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                cleaned_error_output = ansi_escape_pattern.sub('', error_output)
                return f"Inspect command failed:\n{cleaned_error_output}"
        except FileNotFoundError:
            return f"'{GLTF_TRANSFORM_CLI}' command not found. Is it installed and in PATH?"
        except Exception as e:
            return f"Error during inspect: {e}"

    def _update_file_info(self, file_path, before_or_after="before"):
        inspect_str = "N/A" # Προεπιλογή
        if not file_path or not os.path.exists(file_path):
            size_str = "N/A"
        else:
            size_str = self._get_file_size_formatted(file_path)
            inspect_str = self._get_inspect_output(file_path)

        if before_or_after == "before":
            self.info_before_size.set(size_str)
            self.inspect_text_before.config(state=tk.NORMAL)
            self.inspect_text_before.delete('1.0', tk.END)
            self.inspect_text_before.insert(tk.END, inspect_str)
            self.inspect_text_before.config(state=tk.DISABLED)
            
            self.info_after_size.set("N/A")
            self.inspect_text_after.config(state=tk.NORMAL)
            self.inspect_text_after.delete('1.0', tk.END)
            self.inspect_text_after.insert(tk.END, "Pending optimization...")
            self.inspect_text_after.config(state=tk.DISABLED)
        elif before_or_after == "after":
            self.info_after_size.set(size_str)
            self.inspect_text_after.config(state=tk.NORMAL)
            self.inspect_text_after.delete('1.0', tk.END)
            self.inspect_text_after.insert(tk.END, inspect_str)
            self.inspect_text_after.config(state=tk.DISABLED)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(title="Select Input GLB/GLTF", filetypes=[("GLB/GLTF Files", "*.glb *.gltf"), ("All Files", "*.*")])
        if file_path:
            self.input_file_path.set(file_path)
            base, _ = os.path.splitext(file_path)
            self.output_file_path.set(f"{base}_optimized.glb")
            self.status_message.set(f"Input: {os.path.basename(file_path)}. Ready.")
            self.status_label.config(style="Status.App.TLabel")
            self._update_file_info(file_path, "before")

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(title="Save Optimized File As", defaultextension=".glb", filetypes=[("GLB Files", "*.glb"), ("All Files", "*.*")])
        if file_path:
            if not file_path.lower().endswith(".glb"): file_path += ".glb"
            self.output_file_path.set(file_path)
            self.status_message.set("Output path selected. Ready.")
            self.status_label.config(style="Status.App.TLabel")

    def start_optimize_thread(self):
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select input and output files.")
            return
        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file not found: {input_path}")
            return
        if not output_path.lower().endswith(".glb"):
             messagebox.showerror("Error", "Output file must be a .glb file.")
             return

        self._set_ui_busy(True)
        self.progress_bar.start(10)
        self.status_message.set("Starting optimization...")
        self.status_label.config(style="Status.App.TLabel")
        self.info_after_size.set("Processing...")
        self.inspect_text_after.config(state=tk.NORMAL)
        self.inspect_text_after.delete('1.0', tk.END)
        self.inspect_text_after.insert(tk.END, "Optimization in progress...")
        self.inspect_text_after.config(state=tk.DISABLED)

        thread = threading.Thread(target=self._perform_optimization_v414,
                                  args=(input_path, output_path),
                                  daemon=True)
        thread.start()
        self.parent.after(100, self._check_result_queue)

    def _set_ui_busy(self, busy):
        state = tk.DISABLED if busy else tk.NORMAL
        widgets_to_toggle = [
            self.optimize_button, self.browse_input_button, self.browse_output_button,
            self.input_entry, self.output_entry, self.draco_cb, self.texture_cb
        ]
        for widget in widgets_to_toggle: widget.config(state=state)
        texture_options_state = tk.DISABLED if busy else (tk.NORMAL if self.process_textures.get() else tk.DISABLED)
        for child in self.texture_options_frame.winfo_children():
            try: child.config(state=texture_options_state)
            except tk.TclError:
                if isinstance(child, ttk.Scale): child.state(["!disabled" if texture_options_state == tk.NORMAL else "disabled"])
    
    def _update_status(self, message, style="Status.App.TLabel"):
        self.status_message.set(message)
        self.status_label.config(style=style)
        self.parent.update_idletasks()

    def _perform_optimization_v414(self, input_path, output_path):
        try:
            base_output_dir = os.path.dirname(output_path)
            temp_dir_name = f"temp_gltf_{os.path.splitext(os.path.basename(input_path))[0]}_{os.getpid()}"
            temp_dir = os.path.join(base_output_dir, temp_dir_name)
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)
            initial_glb_in_temp = os.path.join(temp_dir, "input_prepared.glb")
            self.result_queue.put(("progress", f"Preparing input: {os.path.basename(input_path)}..."))
            if input_path.lower().endswith(".gltf"):
                cmd_convert_to_glb = [GLTF_TRANSFORM_CLI, "copy", input_path, initial_glb_in_temp]
                result = subprocess.run(cmd_convert_to_glb, capture_output=True, text=True, check=False, encoding='utf-8')
                if result.returncode != 0:
                    self.result_queue.put(("error", f"GLTF to GLB failed: {result.stderr or result.stdout}"))
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return
            else: shutil.copyfile(input_path, initial_glb_in_temp)
            current_processing_file = initial_glb_in_temp

            if self.process_textures.get():
                self.result_queue.put(("progress", "gltf-transform: Compressing textures to WebP..."))
                output_after_webp = os.path.join(temp_dir, "step_webp.glb")
                webp_command = [ GLTF_TRANSFORM_CLI, "webp", current_processing_file, output_after_webp,
                                 "--quality", str(self.webp_quality.get()) ]
                self.result_queue.put(("progress", f"Executing: {' '.join(webp_command)}"))
                result = subprocess.run(webp_command, capture_output=True, text=True, check=False, encoding='utf-8')
                if result.returncode != 0:
                    self.result_queue.put(("error", f"gltf-transform webp failed: {result.stderr or result.stdout}"))
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return
                current_processing_file = output_after_webp
            
            if self.use_draco.get():
                self.result_queue.put(("progress", "gltf-transform: Applying Draco compression..."))
                output_after_draco = os.path.join(temp_dir, "step_draco.glb")
                draco_command = [ GLTF_TRANSFORM_CLI, "draco", current_processing_file, output_after_draco ]
                self.result_queue.put(("progress", f"Executing: {' '.join(draco_command)}"))
                result = subprocess.run(draco_command, capture_output=True, text=True, check=False, encoding='utf-8')
                if result.returncode != 0:
                    self.result_queue.put(("error", f"Draco compression failed: {result.stderr or result.stdout}"))
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return
                current_processing_file = output_after_draco
            
            shutil.copyfile(current_processing_file, output_path)
            self.result_queue.put(("update_after_info_full", output_path)) # Στέλνουμε το path για το inspect
            self.result_queue.put(("success", f"Optimization successful! Output: '{os.path.basename(output_path)}'"))

        except FileNotFoundError:
            self.result_queue.put(("error", f"'{GLTF_TRANSFORM_CLI}' not found. Is it installed and in PATH?"))
        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"Full error traceback in optimizer thread (display inspect logic):\n{tb_str}")
            self.result_queue.put(("error", f"Optimization failed: {str(e)}"))
        finally:
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    # self.result_queue.put(("progress", "Temporary files cleaned up.")) # Λιγότερο verbose
                except Exception as e_clean:
                    self.result_queue.put(("progress", f"Note: Could not fully clean temp files: {e_clean}"))

    def _check_result_queue(self):
        try:
            message_type, message_content = self.result_queue.get_nowait()
            if message_type == "progress":
                self._update_status(message_content)
            elif message_type == "update_after_info_full":
                output_file_path_for_info = message_content
                self._update_file_info(output_file_path_for_info, "after")
            elif message_type == "success":
                self._finalize_ui()
                self._update_status(message_content, "Success.App.TLabel")
                messagebox.showinfo("Success", message_content)
                return 
            elif message_type == "error":
                self._finalize_ui()
                self.info_after_size.set("Error")
                self.inspect_text_after.config(state=tk.NORMAL)
                self.inspect_text_after.delete('1.0', tk.END)
                self.inspect_text_after.insert(tk.END, f"Error during optimization.\nSee console or status for details.")
                self.inspect_text_after.config(state=tk.DISABLED)
                self._update_status(message_content, "Error.App.TLabel")
                messagebox.showerror("Error", message_content)
                return
            
            self.parent.after(100, self._check_result_queue)

        except queue.Empty:
            self.parent.after(100, self._check_result_queue)
        except Exception as e:
            self._finalize_ui()
            tb_str = traceback.format_exc()
            self.info_after_size.set("Error")
            self.inspect_text_after.config(state=tk.NORMAL)
            self.inspect_text_after.delete('1.0', tk.END)
            self.inspect_text_after.insert(tk.END, f"Queue check error: {e}")
            self.inspect_text_after.config(state=tk.DISABLED)
            self._update_status(f"Queue check error: {e}", "Error.App.TLabel")
            print(f"Error checking result queue (display inspect logic): {e}\n{tb_str}")
            messagebox.showerror("Internal Error", f"An error occurred while processing results: {e}")

    def _finalize_ui(self):
        self._set_ui_busy(False)
        self.progress_bar.stop()
        # Δεν χρειάζεται να αλλάξει το status_message εδώ, καθώς θα το έχει κάνει το success/error.

# --- Για αυτόνομη εκτέλεση ---
def main():
    root = tk.Tk()
    app_container = ttk.Frame(root, style="App.TFrame") 
    app_container.pack(fill=tk.BOTH, expand=True)
    app = GLBOptimizerApp(app_container)
    root.mainloop()

if __name__ == '__main__':
    main()