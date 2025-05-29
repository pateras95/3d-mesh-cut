import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import importlib
import traceback
import subprocess
import sys
import os
from functools import partial

# --- Χρωματικό Σχήμα & Γραμματοσειρές ---
BG_COLOR_ROOT = "#e0e0e0"
SIDEBAR_BG = "#2c3e50"
SIDEBAR_FG = "#ecf0f1"
BUTTON_BG = "#3498db" 
BUTTON_FG = "white"
BUTTON_HOVER_BG = "#2980b9"
CONTENT_BG = "#ffffff"  
TEXT_COLOR = "#34495e"   
ERROR_FG = "#e74c3c"
APP_TEXT_COLOR_SECONDARY = "#7f8c8d"

APP_CONTENT_BG = "#f7f9fc" 
APP_TEXT_COLOR_PRIMARY = "#2c3e50"
APP_TEXT_COLOR_SECONDARY = "#7f8c8d"
APP_BUTTON_BG_PRIMARY = "#3498db"
APP_BUTTON_FG_PRIMARY = "white"
APP_BUTTON_HOVER_PRIMARY = "#2980b9"
BUTTON_BG_SECONDARY = "#ecf0f1"


FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_BUTTON = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_TITLE = (FONT_FAMILY, FONT_SIZE_LARGE, "bold")
FONT_LABEL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_LABEL_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_STATUS = (FONT_FAMILY, FONT_SIZE_NORMAL -1, "italic")
FONT_SECTION_TITLE = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold", "underline")

active_button = None
big_block_content_frame = None

class CutterLauncherUI:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.status_label_var = tk.StringVar(value="Ready to launch cutter.")

        content_frame = ttk.Frame(self.parent_frame, style="AppSub.TFrame", padding="15 20")
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        row_idx = 0

        title_label = ttk.Label(content_frame, text="3D Mesh FreeHand Cutter (Vedo)", style="SectionSub.TLabel")
        title_label.grid(row=row_idx, column=0, pady=(0, 20), sticky="w"); row_idx += 1
        
        instructions_text = (
            "This tool will launch the Vedo FreeHand Cutter in a separate window.\n\n"
            "1. Click 'Launch Cutter & Select File'.\n"
            "2. Select your 3D model.\n"
            "3. The Vedo interactive cutting window will open.\n"
            "4. Follow Vedo's on-screen instructions/hotkeys for cutting.\n"
            "   (Often involves drawing a lasso, then pressing 'z' to cut, 'x' to export etc.)\n"
            "5. Close the Vedo window when finished."
        )
        instructions_label = ttk.Label(content_frame, text=instructions_text, style="AppSub.TLabel", justify=tk.LEFT, wraplength=550)
        instructions_label.grid(row=row_idx, column=0, pady=(0, 20), sticky="ew"); row_idx += 1

        launch_button = ttk.Button(content_frame, text="Launch Cutter & Select File", command=self.run_cutter_script, style="PrimarySub.TButton")
        launch_button.grid(row=row_idx, column=0, ipady=8, pady=(10,15), sticky="ew"); row_idx += 1
        
        status_frame = ttk.Frame(content_frame, style="AppSub.TFrame", padding=(0,10,0,0))
        status_frame.grid(row=row_idx, column=0, sticky="ew", pady=(10,0)); row_idx += 1
        status_frame.columnconfigure(0, weight=1)

        status_label = ttk.Label(status_frame, textvariable=self.status_label_var, style="StatusSub.TLabel", anchor="w")
        status_label.grid(row=0, column=0, sticky="ew", padx=(5,0))
        
        self.progress_bar = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        content_frame.rowconfigure(row_idx, weight=1)

    def run_cutter_script(self):
        self.status_label_var.set("Launching cutter script...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,0))
        self.progress_bar.start(10)
        self.parent_frame.update_idletasks()
        
        try:
            script_name_for_cutter = "3d_mesh_cut.py"
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name_for_cutter)

            if not os.path.exists(script_path):
                self.status_label_var.set(f"Error: Script not found at {script_path}")
                messagebox.showerror("Error", f"Cutter script not found:\n{script_path}", parent=self.parent_frame)
                self._finalize_ui(error=True)
                return

            process = subprocess.Popen([sys.executable, script_path], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            self.status_label_var.set("Cutter tool launched. A file dialog should appear from the cutter.")
            self.parent_frame.after(1000, lambda p=process: self._check_process_status(p))

        except Exception as e:
            self.status_label_var.set(f"Error launching cutter: {e}")
            messagebox.showerror("Launch Error", f"Could not launch cutter script:\n{e}", parent=self.parent_frame)
            traceback.print_exc()
            self._finalize_ui(error=True)

    def _check_process_status(self, process):
        if process.poll() is None: 
            self.parent_frame.after(1000, lambda p=process: self._check_process_status(p))
        else: 
            stdout, stderr = process.communicate() 
            if process.returncode == 0:
                self.status_label_var.set("Cutter script finished successfully.")
            else:
                self.status_label_var.set(f"Cutter script exited with error (code {process.returncode}).")
                print(f"--- Cutter Script Output (code {process.returncode}) ---")
                if stdout: print(f"STDOUT:\n{stdout.decode(errors='ignore')}")
                if stderr: print(f"STDERR:\n{stderr.decode(errors='ignore')}")
                print("---------------------------------")
                messagebox.showwarning("Cutter Warning", f"Cutter script exited with code {process.returncode}.\nCheck launcher console for details.", parent=self.parent_frame)
            self._finalize_ui()

    def _finalize_ui(self, error=False):
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        if not error:
            self.status_label_var.set("Ready to launch again or select another tool.")

def run_script(script_name, button_clicked):
    global active_button, big_block_content_frame

    for widget in big_block_content_frame.winfo_children():
        widget.destroy()
    for i in range(big_block_content_frame.grid_size()[0]): big_block_content_frame.columnconfigure(i, weight=0)
    for i in range(big_block_content_frame.grid_size()[1]): big_block_content_frame.rowconfigure(i, weight=0)
    big_block_content_frame.columnconfigure(0, weight=1)
    big_block_content_frame.rowconfigure(0, weight=1)

    if active_button:
        active_button.config(style="Sidebar.TButton")
    active_button = button_clicked
    active_button.config(style="ActiveSidebar.TButton")

    try:
        if script_name == "object_repair":
            script_module = importlib.import_module(script_name)
            app_instance = script_module.MeshRepairApp(big_block_content_frame)
        elif script_name == "gltf_optimizer":
            script_module = importlib.import_module(script_name)
            app_instance = script_module.GLBOptimizerApp(big_block_content_frame)
        elif script_name == "3d_mesh_cut": # ΕΠΑΝΑΦΟΡΑ ΣΤΟ ΑΡΧΙΚΟ ΟΝΟΜΑ
            CutterLauncherUI(big_block_content_frame)
        else:
            placeholder_label = ttk.Label(big_block_content_frame, text=f"UI for '{script_name}' to be implemented here.",
                                          font=FONT_TITLE, style="Content.TLabel")
            placeholder_label.grid(row=0, column=0, pady=20, sticky="nsew")
    except ModuleNotFoundError:
        error_message = f"Error: Script module '{script_name}.py' not found."
        error_label = ttk.Label(big_block_content_frame, text=error_message, style="Error.TLabel")
        error_label.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        if active_button: active_button.config(style="Sidebar.TButton")
    except Exception as e:
        error_message = f"Error loading/running {script_name}: {e}\n\nTraceback:\n{traceback.format_exc()}"
        error_text = tk.Text(big_block_content_frame, wrap=tk.WORD, height=10,
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL), relief=tk.SOLID, borderwidth=1,
                             background=CONTENT_BG, foreground=ERROR_FG)
        error_text.insert(tk.END, error_message)
        error_text.config(state=tk.DISABLED)
        error_text.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        if active_button: active_button.config(style="Sidebar.TButton")

def show_welcome_message():
    global active_button, big_block_content_frame
    for widget in big_block_content_frame.winfo_children():
        widget.destroy()
    
    # Επαναφορά ρυθμίσεων grid για το big_block_content_frame
    # ώστε το περιεχόμενο να μπορεί να κεντραριστεί ή να επεκταθεί σωστά
    for i in range(big_block_content_frame.grid_size()[0]): # columns
        big_block_content_frame.columnconfigure(i, weight=0)
    for i in range(big_block_content_frame.grid_size()[1]): # rows
        big_block_content_frame.rowconfigure(i, weight=0)
    
    # Δίνουμε βάρος στη στήλη και τη σειρά όπου θα μπει το welcome frame
    # για να επιτρέψουμε στο welcome_frame να κεντραριστεί σωστά.
    big_block_content_frame.columnconfigure(0, weight=1)
    big_block_content_frame.rowconfigure(0, weight=1) # Για το welcome_outer_frame
    # big_block_content_frame.rowconfigure(1, weight=1) # Για το info_frame (αν το βάλουμε σε ξεχωριστή σειρά)


    if active_button:
        active_button.config(style="Sidebar.TButton")
        active_button = None

    # Δημιουργία ενός εξωτερικού frame για να βοηθήσει στο κεντράρισμα
    # Αυτό το frame θα πάρει όλο τον διαθέσιμο χώρο και θα κεντράρει το περιεχόμενό του.
    welcome_outer_frame = ttk.Frame(big_block_content_frame, style="Content.TFrame")
    welcome_outer_frame.grid(row=0, column=0, sticky="nsew") # Επεκτείνεται για να γεμίσει το big_block_content_frame

    # Ρυθμίσεις για να κεντραριστεί το περιεχόμενο *μέσα* στο welcome_outer_frame
    welcome_outer_frame.columnconfigure(0, weight=1) # Μία στήλη που παίρνει όλο το πλάτος
    welcome_outer_frame.rowconfigure(0, weight=1)    # Σειρά για το μήνυμα καλωσορίσματος (να πάρει χώρο πάνω)
    welcome_outer_frame.rowconfigure(1, weight=0)    # Σειρά για τις πληροφορίες (να είναι κάτω)
    welcome_outer_frame.rowconfigure(2, weight=1)    # Σειρά για να "σπρώξει" τις πληροφορίες προς τα κάτω (να πάρει χώρο κάτω)


    # Frame για το κυρίως μήνυμα καλωσορίσματος (για να ομαδοποιηθεί με το title)
    welcome_message_frame = ttk.Frame(welcome_outer_frame, style="Content.TFrame")
    welcome_message_frame.grid(row=0, column=0, sticky="s", pady=(0, 20)) # sticky="s" για να πάει προς τα κάτω της σειράς 0

    welcome_title = ttk.Label(
        welcome_message_frame,
        text="Welcome to the Universal 3D Toolkit!",
        font=FONT_TITLE, # Χρησιμοποιούμε το FONT_TITLE
        justify=tk.CENTER,
        style="Content.TLabel"
    )
    welcome_title.pack(pady=(0, 5)) # Pack μέσα στο μικρό frame

    welcome_subtitle = ttk.Label(
        welcome_message_frame,
        text="Select a tool from the sidebar to begin.",
        font=FONT_LABEL, # Χρησιμοποιούμε το FONT_LABEL
        justify=tk.CENTER,
        style="Content.TLabel"
    )
    welcome_subtitle.pack()


    # Frame για τις πληροφορίες σου (για να είναι ομαδοποιημένες και κάτω)
    info_frame = ttk.Frame(welcome_outer_frame, style="Content.TFrame")
    info_frame.grid(row=1, column=0, sticky="n", pady=(10, 0)) # sticky="n" για να πάει προς τα πάνω της σειράς 1

    # Στυλ για τις πληροφορίες σου (αν δεν υπάρχει ήδη)
    style.configure("CreatorInfo.TLabel", background=CONTENT_BG, foreground=APP_TEXT_COLOR_SECONDARY, font=(FONT_FAMILY, FONT_SIZE_NORMAL -1))

    creator_name_label = ttk.Label(
        info_frame,
        text="Created by: Konstantinos Kalyvas",
        style="CreatorInfo.TLabel"
    )
    creator_name_label.pack()

    academic_id_label = ttk.Label(
        info_frame,
        text="Academic ID: ic1200008",
        style="CreatorInfo.TLabel"
    )
    academic_id_label.pack()

root = tk.Tk()
root.title("Universal 3D Toolkit")
root.geometry("1200x800")
root.configure(bg=BG_COLOR_ROOT)

style = ttk.Style()
try: style.theme_use('clam')
except tk.TclError: print("Clam theme not available, using default.")

style.configure("Sidebar.TFrame", background=SIDEBAR_BG)
style.configure("Sidebar.TLabel", background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=FONT_TITLE, padding=(0, 10, 0, 10))
style.configure("Sidebar.TButton", font=FONT_BUTTON, background=BUTTON_BG, foreground=BUTTON_FG, borderwidth=0, focuscolor=SIDEBAR_BG, padding=(20, 10))
style.map("Sidebar.TButton", background=[('active', BUTTON_HOVER_BG), ('pressed', BUTTON_HOVER_BG), ('hover', BUTTON_HOVER_BG)], foreground=[('active', BUTTON_FG), ('pressed', BUTTON_FG), ('hover', BUTTON_FG)], relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])
style.configure("ActiveSidebar.TButton", font=FONT_BUTTON, background=BUTTON_HOVER_BG, foreground=BUTTON_FG, borderwidth=0, relief=tk.FLAT, padding=(20, 10))
style.map("ActiveSidebar.TButton", background=[('active', BUTTON_HOVER_BG), ('pressed', BUTTON_HOVER_BG)], foreground=[('active', BUTTON_FG), ('pressed', BUTTON_FG)])
style.configure("Content.TFrame", background=CONTENT_BG)
style.configure("Content.TLabel", background=CONTENT_BG, foreground=TEXT_COLOR, font=FONT_LABEL)
style.configure("Error.TLabel", background=CONTENT_BG, foreground=ERROR_FG, font=FONT_LABEL)

# Styles για το CutterLauncherUI και άλλα sub-apps
style.configure("AppSub.TFrame", background=APP_CONTENT_BG)
style.configure("SectionSub.TLabel", background=APP_CONTENT_BG, foreground=APP_TEXT_COLOR_PRIMARY, font=FONT_SECTION_TITLE)
style.configure("AppSub.TLabel", background=APP_CONTENT_BG, foreground=APP_TEXT_COLOR_PRIMARY, font=FONT_LABEL) # Για το instructions_label
style.configure("PrimarySub.TButton", font=FONT_BUTTON, background=APP_BUTTON_BG_PRIMARY, foreground=APP_BUTTON_FG_PRIMARY, padding=(15,10))
style.map("PrimarySub.TButton", background=[('active', APP_BUTTON_HOVER_PRIMARY), ('pressed', APP_BUTTON_HOVER_PRIMARY)])
style.configure("StatusSub.TLabel", background=APP_CONTENT_BG, foreground=APP_TEXT_COLOR_SECONDARY, font=FONT_STATUS)
style.configure("ProgressSub.TProgressbar", troughcolor=BUTTON_BG_SECONDARY, background=APP_BUTTON_BG_PRIMARY) # Χρησιμοποιεί το BUTTON_BG_SECONDARY

sidebar = ttk.Frame(root, width=250, style="Sidebar.TFrame")
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)
app_title_label = ttk.Label(sidebar, text="TOOLKIT", style="Sidebar.TLabel", anchor=tk.CENTER)
app_title_label.pack(pady=(20, 10), fill=tk.X)
separator = ttk.Separator(sidebar, orient='horizontal')
separator.pack(fill='x', padx=10, pady=10)

button1 = ttk.Button(sidebar, text="Object Repair", style="Sidebar.TButton")
button1.config(command=partial(run_script, "object_repair", button1))
button1.pack(pady=5, padx=20, fill=tk.X)

button2 = ttk.Button(sidebar, text="GLTF Optimizer", style="Sidebar.TButton")
button2.config(command=partial(run_script, "gltf_optimizer", button2))
button2.pack(pady=5, padx=20, fill=tk.X)

button3 = ttk.Button(sidebar, text="3D Mesh Cut", style="Sidebar.TButton")
button3.config(command=partial(run_script, "3d_mesh_cut", button3))
button3.pack(pady=5, padx=20, fill=tk.X)

big_block_container = ttk.Frame(root, style="Content.TFrame", padding=10)
big_block_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

big_block_content_frame = ttk.Frame(big_block_container, style="Content.TFrame")
big_block_content_frame.pack(fill=tk.BOTH, expand=True)
big_block_content_frame.columnconfigure(0, weight=1)
big_block_content_frame.rowconfigure(0, weight=1)

show_welcome_message()
root.mainloop()