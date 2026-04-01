import os
import requests
import zipfile
from io import BytesIO
import shutil
import sys
import ctypes
import winreg

# -----------------------------
# Settings
# -----------------------------
zip_url = "https://github.com/NishVish/PySwiss/archive/refs/heads/main.zip"
target_dir = "C:\\PySwiss"

# -----------------------------
# Download and flatten repo
# -----------------------------
def download_repo_flat():
    try:
        if os.path.exists(target_dir):
            print(f"Directory already exists: {target_dir}")
        else:
            os.makedirs(target_dir)

        print("Downloading repository...")
        r = requests.get(zip_url)
        r.raise_for_status()

        print("Extracting files...")
        with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
            temp_dir = os.path.join(target_dir, "temp_extract")
            zip_ref.extractall(temp_dir)

            extracted_root = os.path.join(temp_dir, "PySwiss-main")
            for item in os.listdir(extracted_root):
                s = os.path.join(extracted_root, item)
                d = os.path.join(target_dir, item)
                shutil.move(s, d)

            shutil.rmtree(temp_dir)

        print(f"All files moved directly into {target_dir}")

    except Exception as e:
        print("Error:", e)

# -----------------------------
# Add context menu entry
# -----------------------------
def add_context_menu():
    try:
        python_exe = sys.executable
        pyrunner_path = os.path.join(target_dir, "pyrunner.py")

        key_path = r"Directory\Background\shell\RunPyRunner"
        command_path = key_path + r"\command"

        # Create main key
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Run PyRunner")

        # Create command key
        cmd = f'"{python_exe}" "{pyrunner_path}" "%V"'
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path) as cmd_key:
            winreg.SetValue(cmd_key, "", winreg.REG_SZ, cmd)

        print("Context menu added successfully!")

    except PermissionError:
        print("Access denied. Please run this script as Administrator!")
    except Exception as e:
        print("Failed to add context menu:", e)

# -----------------------------
# Check admin
# -----------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    download_repo_flat()

    if not is_admin():
        print("Requesting Administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    add_context_menu()