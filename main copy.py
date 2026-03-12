import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import tempfile
import os
import sys
import threading

# --- UI Theme Colors ---
BG_DARK = "#1e1e1e"
BG_PANEL = "#1a1a1a"
BG_TOOLBAR = "#2d2d2d"
FG_TEXT = "#d4d4d4"
ACCENT = "#007acc"
EXE_ACCENT = "#28a745"
TEST_ACCENT = "#6a1b9a"  # Purple for Test File button
HTML_ACCENT = "#ff6f00"  # Orange for HTML file
OUTPUT_FG = "#9cdcfe"

# Global variable to track the currently open file
current_open_file = None
project_dir = os.getcwd()  # Default project directory
SCRIPT_DIR = os.path.join(project_dir, "script")  # Folder for scripts

def setup_scripts_folder():
    """Ensure the script folder exists and populate it from the repo."""
    os.makedirs(SCRIPT_DIR, exist_ok=True)

    # List of scripts in the repo to download
    scripts_to_download = ["example1.py", "example2.py"]  # Replace with actual repo scripts

    for script_name in scripts_to_download:
        local_path = os.path.join(SCRIPT_DIR, script_name)
        if not os.path.exists(local_path):
            try:
                url = REPO_SCRIPT_URL + script_name
                urllib.request.urlretrieve(url, local_path)
                # update_output may not exist yet, so just print for now
                print(f"Downloaded script: {script_name}")
            except Exception as e:
                print(f"Failed to download {script_name}: {e}")


                
# --- Functions ---
def update_output(text):
    output.config(state="normal")
    output.delete("1.0", tk.END)
    output.insert(tk.END, text)
    output.config(state="disabled")
    output.see(tk.END)

def run_code(event=None):
    code = editor.get("1.0", tk.END)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp:
        temp.write(code)
        temp_path = temp.name
    try:
        result = subprocess.run([sys.executable, temp_path], capture_output=True, text=True, encoding="utf-8")
        update_output(result.stdout + (f"\n--- ERRORS ---\n{result.stderr}" if result.stderr else ""))
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

def save_file(event=None):
    global current_open_file
    if current_open_file:
        with open(current_open_file, "w", encoding="utf-8") as f:
            f.write(editor.get("1.0", tk.END).strip())
        root.title(f"PyRunner - {os.path.basename(current_open_file)} (Saved)")
    else:
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            current_open_file = file_path
            save_file()

def create_test_file():
    """Creates test.txt in project directory."""
    file_path = os.path.join(project_dir, "test.txt")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("this is test File")
        update_output(f"Successfully created test file:\n{file_path}")
        messagebox.showinfo("Success", f"File created:\n{file_path}")
        editor.delete("1.0", tk.END)
        editor.insert("1.0", "this is test File")
    except Exception as e:
        update_output(f"Error creating file: {e}")
        messagebox.showerror("Error", f"Could not create file: {e}")

def create_html_file():
    """Creates an HTML file from editor content."""
    html_code = editor.get("1.0", tk.END).strip()
    if not html_code:
        messagebox.showwarning("Empty Editor", "Please paste some HTML before creating a file.")
        return

    file_name = simpledialog.askstring("File Name", "Enter HTML file name (without .html):")
    if not file_name:
        return
    if not file_name.lower().endswith(".html"):
        file_name += ".html"

    file_path = os.path.join(project_dir, file_name)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_code)
        update_output(f"HTML file successfully created:\n{file_path}")
        messagebox.showinfo("Success", f"HTML file created:\n{file_path}")
    except Exception as e:
        update_output(f"Error creating HTML file: {e}")
        messagebox.showerror("Error", f"Could not create file: {e}")

def make_exe():
    code = editor.get("1.0", tk.END).strip()
    if not code:
        messagebox.showwarning("Empty Editor", "Please write some code before building an EXE.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        update_output("Starting Build Process... Please wait.")
        threading.Thread(target=run_pyinstaller, args=(file_path,), daemon=True).start()

def run_pyinstaller(file_path):
    try:
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            update_output(f"SUCCESS!\nFile in 'dist' folder near:\n{os.path.dirname(file_path)}")
        else:
            update_output(f"BUILD FAILED:\n{result.stderr}")
    except Exception as e:
        update_output(f"Error: {str(e)}")

# --- Root Window ---
root = tk.Tk()
root.title("Python IDE & HTML/EXE Creator")
root.geometry("1200x700")
root.configure(bg=BG_DARK)

# --- Toolbar ---
toolbar = tk.Frame(root, bg=BG_TOOLBAR, height=40)
toolbar.pack(side="top", fill="x")
btn_params = {"relief": "flat", "font": ("Segoe UI", 9), "padx": 15}

run_btn = tk.Button(toolbar, text="Run ▶", bg=ACCENT, fg="white", command=run_code, **btn_params)
run_btn.pack(side="left", padx=5, pady=5)

save_btn = tk.Button(toolbar, text="Save 💾", bg=BG_DARK, fg=FG_TEXT, command=save_file, **btn_params)
save_btn.pack(side="left", padx=5, pady=5)

exe_btn = tk.Button(toolbar, text="Build EXE 📦", bg=EXE_ACCENT, fg="white", command=make_exe, **btn_params)
exe_btn.pack(side="left", padx=5, pady=5)

test_btn = tk.Button(toolbar, text="Test File 📄", bg=TEST_ACCENT, fg="white", command=create_test_file, **btn_params)
test_btn.pack(side="left", padx=5, pady=5)

html_btn = tk.Button(toolbar, text="Create HTML 🌐", bg=HTML_ACCENT, fg="white", command=create_html_file, **btn_params)
html_btn.pack(side="left", padx=5, pady=5)

# --- Paned Window Layout ---
pw = tk.PanedWindow(root, orient="horizontal", bg="#333", sashwidth=4, sashrelief="flat")
pw.pack(fill="both", expand=True)


# --- Scripts Side Panel ---
scripts_frame = tk.Frame(pw, bg="#252526", width=200)
scripts_label = tk.Label(scripts_frame, text="Scripts", bg="#252526", fg="white", font=("Segoe UI", 10, "bold"))
scripts_label.pack(anchor="nw", padx=10, pady=5)

scripts_listbox = tk.Listbox(scripts_frame, bg="#333", fg="white", font=("Consolas", 10), selectbackground=ACCENT,
                             activestyle="none", borderwidth=0, highlightthickness=0)
scripts_listbox.pack(fill="both", expand=True, padx=5, pady=5)

def refresh_scripts_list():
    scripts_listbox.delete(0, tk.END)
    scripts_dir = os.path.join(project_dir, "script")
    os.makedirs(scripts_dir, exist_ok=True)
    for file in os.listdir(scripts_dir):
        if file.endswith(".py"):
            scripts_listbox.insert(tk.END, file)

def load_selected_script(event):
    selection = scripts_listbox.curselection()
    if selection:
        file_name = scripts_listbox.get(selection[0])
        file_path = os.path.join(project_dir, "script", file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                editor.delete("1.0", tk.END)
                editor.insert(tk.END, f.read())
            global current_open_file
            current_open_file = file_path
            root.title(f"PyRunner - {file_name}")
        except Exception as e:
            update_output(f"Error loading file: {e}")

scripts_listbox.bind("<<ListboxSelect>>", load_selected_script)

# Initial population
# After scripts_listbox, editor, and output are created
setup_scripts_folder()
refresh_scripts_list()  # Populate the side panel


editor_frame = tk.Frame(pw, bg=BG_DARK)
editor = tk.Text(editor_frame, wrap="none", font=("Consolas", 11), bg=BG_DARK, fg=FG_TEXT,
                 insertbackground="white", padx=15, pady=15, borderwidth=0, undo=True)
editor.pack(side="left", fill="both", expand=True)

output_frame = tk.Frame(pw, bg=BG_PANEL)
output = tk.Text(output_frame, wrap="word", font=("Consolas", 10), bg=BG_PANEL, fg=OUTPUT_FG,
                 borderwidth=0, padx=15, pady=10, state="disabled")
output.pack(fill="both", expand=True)

pw.add(scripts_frame, width=200)
pw.add(editor_frame, width=700)
pw.add(output_frame, width=500)

# --- Handle command line arguments ---
if len(sys.argv) > 1:
    clicked_file = sys.argv[1]
    if os.path.isfile(clicked_file):
        try:
            with open(clicked_file, "r", encoding="utf-8") as f:
                editor.delete("1.0", tk.END)
                editor.insert(tk.END, f.read())
            current_open_file = clicked_file
            project_dir = os.path.dirname(clicked_file)
            root.title(f"PyRunner - {os.path.basename(clicked_file)}")
        except Exception as e:
            update_output(f"Error loading file: {e}")
    elif os.path.isdir(clicked_file):
        project_dir = clicked_file
        update_output(f"Project Folder opened: {clicked_file}")

# --- Shortcuts ---
root.bind("<Control-Return>", run_code)
root.bind("<Control-s>", save_file)

root.mainloop()
