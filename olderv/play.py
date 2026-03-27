import tkinter as tk
from tkinter import filedialog, font
import subprocess
import tempfile
import os
import sys

# --- UI Theme Colors ---
BG_DARK = "#1e1e1e"      # Editor Background
BG_PANEL = "#1a1a1a"     # Output Background
BG_TOOLBAR = "#2d2d2d"   # Toolbar Background
FG_TEXT = "#d4d4d4"      # Standard Gray Text
ACCENT = "#007acc"       # VS Code Blue
OUTPUT_FG = "#9cdcfe"    # Light Blue Output

def run_code(event=None):
    code = editor.get("1.0", tk.END)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True, text=True, encoding="utf-8"
        )
        output.config(state="normal")
        output.delete("1.0", tk.END)
        # Combine stdout and stderr
        output.insert(tk.END, result.stdout)
        if result.stderr:
            output.insert(tk.END, "\n--- ERRORS ---\n" + result.stderr)
        output.config(state="disabled")
        output.see(tk.END) # Auto-scroll to bottom

    except Exception as e:
        output.config(state="normal")
        output.insert(tk.END, f"System Error: {str(e)}")
        output.config(state="disabled")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            editor.delete("1.0", tk.END)
            editor.insert(tk.END, f.read())

# --- Root Window ---
root = tk.Tk()
root.title("Python Side-by-Side")
root.geometry("1200x700")
root.configure(bg=BG_DARK)

# --- Toolbar ---
toolbar = tk.Frame(root, bg=BG_TOOLBAR, height=40)
toolbar.pack(side="top", fill="x")

# Styled Buttons
btn_params = {"relief": "flat", "font": ("Segoe UI", 9), "padx": 15}
run_btn = tk.Button(toolbar, text="Run ▶", bg=ACCENT, fg="white", 
                    activebackground="#005a9e", command=run_code, **btn_params)
run_btn.pack(side="left", padx=5, pady=5)

open_btn = tk.Button(toolbar, text="Open File", bg=BG_DARK, fg=FG_TEXT, 
                     command=open_file, **btn_params)
open_btn.pack(side="left", padx=5, pady=5)

# --- Horizontal PanedWindow ---
# Changed orient to "horizontal" to put panels side-by-side
pw = tk.PanedWindow(root, orient="horizontal", bg="#333", sashwidth=4, sashrelief="flat")
pw.pack(fill="both", expand=True)

# Editor Container (Left)
editor_frame = tk.Frame(pw, bg=BG_DARK)
editor = tk.Text(editor_frame, wrap="none", font=("Consolas", 11), 
                 bg=BG_DARK, fg=FG_TEXT, insertbackground="white",
                 padx=15, pady=15, borderwidth=0, undo=True)
editor.pack(side="left", fill="both", expand=True)

# Output Container (Right)
output_frame = tk.Frame(pw, bg=BG_PANEL)
output_label = tk.Label(output_frame, text="TERMINAL OUTPUT", bg=BG_PANEL, 
                        fg="#666", font=("Segoe UI", 8, "bold"))
output_label.pack(side="top", anchor="nw", padx=10, pady=(5, 0))

output = tk.Text(output_frame, wrap="word", font=("Consolas", 10), 
                 bg=BG_PANEL, fg=OUTPUT_FG, borderwidth=0, 
                 padx=15, pady=10, state="disabled")
output.pack(side="bottom", fill="both", expand=True)

# Add to PanedWindow
pw.add(editor_frame, width=700) # Default editor width
pw.add(output_frame, width=500) # Default output width

# Bindings
root.bind("<Control-Return>", run_code)

root.mainloop()