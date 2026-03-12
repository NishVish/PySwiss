import os
import sys
import winreg
import urllib.request
import subprocess

MENU_NAME = "PySwiss"
MAIN_PY_URL = "https://raw.githubusercontent.com/NishVish/PySwiss/main/main.py"

INSTALL_DIR = os.path.join(os.environ["LOCALAPPDATA"], "PySwiss")
TARGET_MAIN = os.path.join(INSTALL_DIR, "main.py")
PYTHON_EXE = sys.executable


def ensure_installed():

    os.makedirs(INSTALL_DIR, exist_ok=True)

    if not os.path.exists(TARGET_MAIN):
        urllib.request.urlretrieve(MAIN_PY_URL, TARGET_MAIN)

    entries = [
        (r"Software\Classes\*\shell", "%1"),
        (r"Software\Classes\Directory\shell", "%1"),
        (r"Software\Classes\Directory\Background\shell", "%V")
    ]

    for reg_path, arg in entries:

        key_path = rf"{reg_path}\{MENU_NAME}"
        cmd = f'"{PYTHON_EXE}" "{os.path.abspath(__file__)}" {arg}'

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, MENU_NAME)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path + r"\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, cmd)


def run_now(target):

    subprocess.Popen(
        [PYTHON_EXE, TARGET_MAIN, target],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


if __name__ == "__main__":

    ensure_installed()

    if len(sys.argv) > 1:
        run_now(sys.argv[1])