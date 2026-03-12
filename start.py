import os
import sys
import ctypes
import shutil
import urllib.request
import winreg
import subprocess

APP = "PySwiss"
INSTALL_DIR = r"C:\Program Files\PySwiss"

START_EXE = os.path.join(INSTALL_DIR, "start.exe")
MAIN_PY = os.path.join(INSTALL_DIR, "main.py")
RUN_CMD = os.path.join(INSTALL_DIR, "run.cmd")

MAIN_URL = "https://raw.githubusercontent.com/NishVish/PySwiss/main/main.py"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1
    )
    sys.exit()

def setup():

    # Only request admin if install folder does not exist
    if not os.path.exists(INSTALL_DIR):

        if not is_admin():
            elevate()

        os.makedirs(INSTALL_DIR, exist_ok=True)

        shutil.copy(sys.executable, START_EXE)

        urllib.request.urlretrieve(MAIN_URL, MAIN_PY)

        with open(RUN_CMD, "w") as f:
            f.write(f'@echo off\npython "%~dp0main.py" %*')

        # Add right click menu
        key = r"Software\Classes\*\shell\PySwiss"

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key) as k:
            winreg.SetValue(k, "", winreg.REG_SZ, "PySwiss")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key + r"\command") as k:
            winreg.SetValue(k, "", winreg.REG_SZ, f'"{RUN_CMD}" "%1"')

def run_main(target):

    subprocess.Popen(["python", MAIN_PY, target])


if __name__ == "__main__":

    setup()

    if len(sys.argv) > 1:
        run_main(sys.argv[1])


