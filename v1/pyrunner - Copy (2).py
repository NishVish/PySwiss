import tkinter as tk
from tkinter import filedialog, font, messagebox
import subprocess
import tempfile
import os
import sys
import threading # To keep the UI responsive during build

# --- UI Theme Colors ---
BG_DARK = "#1e1e1e"
BG_PANEL = "#1a1a1a"
BG_TOOLBAR = "#2d2d2d"
FG_TEXT = "#d4d4d4"
ACCENT = "#007acc"
EXE_ACCENT = "#28a745" # Green for Build button
OUTPUT_FG = "#9cdcfe"

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
        update_output(result.stdout + (f"\n--- ERRORS ---\n{result.stderr}" if result.stderr else ""))
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

def update_output(text):
    output.config(state="normal")
    output.delete("1.0", tk.END)
    output.insert(tk.END, text)
    output.config(state="disabled")
    output.see(tk.END)

def make_exe():
    code = editor.get("1.0", tk.END).strip()
    if not code:
        messagebox.showwarning("Empty Editor", "Please write some code before building an EXE.")
        return

    # Ask user where to save the .py file (PyInstaller needs a physical file)
    file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Run PyInstaller in a separate thread so the UI doesn't freeze
        update_output("Starting Build Process... Please wait.\n(This may take a minute)")
        threading.Thread(target=run_pyinstaller, args=(file_path,), daemon=True).start()

def run_pyinstaller(file_path):
    try:
        # --onefile: bundle into a single exe
        # --noconsole: hide the black cmd window when running the result
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", file_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            update_output(f"SUCCESS!\nYour executable is in the 'dist' folder near your saved file:\n{os.path.dirname(file_path)}")
            messagebox.showinfo("Build Complete", "EXE created successfully in the 'dist' folder.")
        else:
            update_output(f"BUILD FAILED:\n{result.stderr}")
    except Exception as e:
        update_output(f"System Error: {str(e)}\n\nMake sure you have pyinstaller installed (pip install pyinstaller)")

# --- Root Window ---
root = tk.Tk()
root.title("Python IDE & EXE Creator")
root.geometry("1200x700")
root.configure(bg=BG_DARK)

# --- Toolbar ---
toolbar = tk.Frame(root, bg=BG_TOOLBAR, height=40)
toolbar.pack(side="top", fill="x")

btn_params = {"relief": "flat", "font": ("Segoe UI", 9), "padx": 15}

run_btn = tk.Button(toolbar, text="Run ▶", bg=ACCENT, fg="white", command=run_code, **btn_params)
run_btn.pack(side="left", padx=5, pady=5)

exe_btn = tk.Button(toolbar, text="Build EXE 📦", bg=EXE_ACCENT, fg="white", command=make_exe, **btn_params)
exe_btn.pack(side="left", padx=5, pady=5)

# --- Layout ---
pw = tk.PanedWindow(root, orient="horizontal", bg="#333", sashwidth=4, sashrelief="flat")
pw.pack(fill="both", expand=True)

editor_frame = tk.Frame(pw, bg=BG_DARK)
editor = tk.Text(editor_frame, wrap="none", font=("Consolas", 11), bg=BG_DARK, fg=FG_TEXT, insertbackground="white", padx=15, pady=15, borderwidth=0, undo=True)
editor.pack(side="left", fill="both", expand=True)

output_frame = tk.Frame(pw, bg=BG_PANEL)
output = tk.Text(output_frame, wrap="word", font=("Consolas", 10), bg=BG_PANEL, fg=OUTPUT_FG, borderwidth=0, padx=15, pady=10, state="disabled")
output.pack(fill="both", expand=True)

pw.add(editor_frame, width=700)
pw.add(output_frame, width=500)

root.bind("<Control-Return>", run_code)
root.mainloop()