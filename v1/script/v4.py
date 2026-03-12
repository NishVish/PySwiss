# ==============================
# System Imports
# ==============================
import sys
import os
import logging
import socket
import io
import base64
import webbrowser
import threading
import time
import platform
import subprocess

# ==============================
# Third-Party Imports
# ==============================
from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import qrcode
import requests
from colorama import Fore, Style, init


# ==============================
# Safe UTF-8 Configuration
# ==============================
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==============================
# Initialize Colorama
# ==============================
init(autoreset=True)


# ==============================
# Base Directory Detection
# Works for:
# - PyInstaller EXE
# - Normal Python script
# - Jupyter Notebook
# ==============================
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)

elif '__file__' in globals():
    base_dir = os.path.dirname(os.path.abspath(__file__))

else:
    base_dir = os.getcwd()


# ==============================
# Shared Files Directory
# ==============================
SHARED_DIR = os.path.join(base_dir, "shared_files")
os.makedirs(SHARED_DIR, exist_ok=True)


# ==============================
# Logging Configuration
# ==============================
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("flask.app").setLevel(logging.ERROR)


# ==============================
# Flask App Instance
# ==============================
app = Flask(__name__)


# ==============================
# Online Layout Dependency
# ==============================
DEP_JSON_URL = "https://raw.githubusercontent.com/NishVish/Project-Dependency/main/dependency.json"

# ==============================
# Fallback HTML
# ==============================

fallback_html  = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📁 PC-Phone File Transfer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --success: #22c55e;
            --error: #ef4444;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 600px;
        }

        /* Developer Info Header */
        .developer-info {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: white;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
            font-size: 0.9rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .developer-info a {
            color: #e0e7ff;
            text-decoration: none;
            font-weight: 600;
        }

        .card {
            background: var(--card-bg);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border: 1px solid #f1f5f9;
        }

        h2 {
            font-size: 1.25rem;
            margin-top: 0;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* QR Section */
        .qr-section {
            text-align: center;
        }

        .qr-section img {
            border: 8px solid #f1f5f9;
            border-radius: 12px;
            transition: transform 0.3s ease;
        }

        .qr-section img:hover {
            transform: scale(1.02);
        }

        .url-text {
            display: block;
            margin-top: 12px;
            color: var(--text-sub);
            font-size: 0.85rem;
            word-break: break-all;
        }

        /* File List */
        ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        li {
            background: #f8fafc;
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #edf2f7;
            transition: background 0.2s;
        }

        li:hover {
            background: #f1f5f9;
        }

        .file-name {
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-main);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 70%;
        }

        /* Buttons */
        button, .btn-link {
            padding: 8px 16px;
            border: none;
            background-color: var(--primary);
            color: white;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
        }

        button:hover, .btn-link:hover {
            background-color: var(--primary-hover);
            transform: translateY(-1px);
        }

        .btn-folder {
            width: 100%;
            background-color: #f1f5f9;
            color: var(--text-main);
            margin-bottom: 15px;
            border: 1px solid #e2e8f0;
        }

        .btn-folder:hover {
            background-color: #e2e8f0;
        }

        /* Upload Section */
        input[type="file"] {
            width: 100%;
            padding: 10px;
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 10px;
            margin-bottom: 15px;
            box-sizing: border-box;
        }

        progress {
            width: 100%;
            height: 10px;
            border-radius: 10px;
            overflow: hidden;
            border: none;
            margin-top: 15px;
        }

        progress::-webkit-progress-bar { background-color: #f1f5f9; }
        progress::-webkit-progress-value { background-color: var(--primary); }

        #statusText {
            font-size: 0.85rem;
            margin-top: 10px;
            text-align: center;
            font-weight: 600;
        }

        @media (max-width: 480px) {
            body { padding: 10px; }
            .card { padding: 16px; }
            li { flex-direction: column; align-items: flex-start; gap: 10px; }
            .file-name { max-width: 100%; }
        }
    </style>
</head>
<body>

    <div class="container">
    <h1>Backup Layout</h1>
        <div class="developer-info">
            🚀 <strong>Nishant Vishwakarma</strong> • 
            <a href="https://github.com/NishVish" target="_blank">🐙 GitHub Profile</a> ftp:v.3.3
        </div>

        <div class="card qr-section">
            <h2>📱 Phone Access</h2>
            <img src="data:image/png;base64,{{ qr_code_img }}" alt="QR Code" width="180">
            <span class="url-text">Link: <a href="{{ url }}" style="color: var(--primary);">{{ url }}</a></span>
        </div>

        <div class="card">
            <h2>📁 Shared Files</h2>
            
            <form method="POST" action="/open_folder">
                <button type="submit" class="btn-folder">📂 Open Shared Folder</button>
            </form>

            {% if files %}
            <ul>
                {% for file in files %}
                <li>
                    <span class="file-name" title="{{ file }}">{{ file }}</span>
                    <a href="/download/{{ file }}" class="btn-link">Download</a>
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p style="text-align: center; color: var(--text-sub); font-size: 0.9rem;">Shared folder is empty.</p>
            {% endif %}
        </div>

        <div class="card">
            <h2>📤 Send to PC</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" name="files" id="fileInput" multiple required>
                <button type="submit" style="width: 100%; padding: 12px;">Start Upload</button>
            </form>

            <progress id="uploadProgress" value="0" max="100" style="display: none;"></progress>
            <p id="statusText"></p>
        </div>
    </div>

    <script>
    document.getElementById('uploadForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const files = document.getElementById('fileInput').files;
        if (!files.length) return;

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);

        const progressBar = document.getElementById('uploadProgress');
        const statusText = document.getElementById('statusText');
        progressBar.style.display = 'block';

        xhr.upload.onprogress = function (e) {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                progressBar.value = percent;
                statusText.style.color = "var(--primary)";
                statusText.innerText = `📤 Uploading: ${Math.round(percent)}%`;
            }
        };

        xhr.onload = function () {
            if (xhr.status === 200) {
                statusText.style.color = "var(--success)";
                statusText.innerText = "✅ Done! Refreshing list...";
                setTimeout(() => { window.location.reload(); }, 1200);
            } else {
                statusText.style.color = "var(--error)";
                statusText.innerText = "❌ Failed to upload.";
            }
        };

        xhr.onerror = function () {
            statusText.style.color = "var(--error)";
            statusText.innerText = "❌ Network error.";
        };

        xhr.send(formData);
    });
    </script>
</body>
</html>
    '''
    

# ==============================
# Fetch Layout URL
# ==============================
layout_url = None
try:
    dep_data = requests.get(DEP_JSON_URL, timeout=3).json()
    layout_url = dep_data.get("ftp", [None])[0]
except Exception as e:
    print("Could not fetch dependency.json:", e)

print("Layout URL:", layout_url)

# ==============================
# Utilities
# ==============================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def generate_qr_codemain(link):
    img = qrcode.make(link)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

# Utility: Generate QR Code as base64 string
def generate_qr_code(link):
    import qrcode
    img = qrcode.make(link)
    path = "qr_code.png"
    img.save(path)
    return path

    
# ==============================
# Flask Route
# ==============================
@app.route("/")
def index():  # <-- renamed from "index" to "main_index"
    # Try remote HTML
    html_content = None
    if layout_url:
        try:
            html_content = requests.get(layout_url, timeout=3).text
        except Exception as e:
            print("Failed to fetch remote layout:", e)

    # Fallback if remote fails
    if not html_content:
        html_content = fallback_html

    # Variables to inject
    local_ip = get_local_ip()
    url = f"http://{local_ip}:8000"
    qr_code_img = generate_qr_codemain(url)
    files = os.listdir(SHARED_DIR)

    return render_template_string(html_content, qr_code_img=qr_code_img, url=url, files=files)



@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory(SHARED_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404



@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files')
    for file in uploaded_files:
        if file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(SHARED_DIR, filename))
    return redirect(url_for('index'))



@app.route('/health')
def health():
    return {"status": "ok"}, 200
    
    


@app.route('/open_folder', methods=['POST'])
def open_folder():
    import platform
    import subprocess
    folder_path = SHARED_DIR

    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", folder_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", folder_path])
        return '', 204  # No Content
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...', 200


def open_browser():
    ip = get_local_ip()
    webbrowser.open(f"http://{ip}:9835")

def open_image(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux
        subprocess.run(["xdg-open", path])

def open_browser(url):
    webbrowser.open(url)


def show_menu(url, image_path):
    while True:
        print("\n📁 File Transfer App is Ready!")
        print(f"\nURL: {url}")
        print("\nChoose an option:")
        print("[1] 🖼  Show QR code image")
        print("[2] 🌐 Open in browser")
        print("[3] ❌ Exit and stop server")
        print("[4] 👨‍💻 Developer Info")  # NEW option added

        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            open_image(image_path)
        elif choice == '2':
            open_browser(url)
        elif choice == '3':
            print("\n🛑 Exiting... Stopping server.")
            import os
            os._exit(0)  # forcefully terminates process, stops server and releases port

        elif choice == '4':
            developerInfo()
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


def karmant():
    print(r"""
  _  __                                _   
 | |/ /__ _ _ __ _ __ ___   __ _ _ __ | |_ 
 | ' // _` | '__| '_ ` _ \ / _` | '_ \| __|
 | . \ (_| | |  | | | | | | (_| | | | | |_ 
 |_|\_\__,_|_|  |_| |_| |_|\__,_|_| |_|\__|
                                          
""")

def developerInfo():
    name = "Nishant Vishwakarma"
    githublink = "https://github.com/NishVish"

    print(f"\n{Fore.CYAN}{Style.BRIGHT}🚀✨ Developer Info ✨🚀")
    print(f"{Fore.YELLOW}👤 Name: {Fore.GREEN}{name}")
    print(f"{Fore.YELLOW}🐙 GitHub: {Fore.BLUE}{githublink}")
    print(f"{Fore.MAGENTA}🌟 Thanks for checking out the project!\n")



def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


host = get_local_ip()
port = 8000
def run_server():
    print(f"Starting Flask server at http://{host}:{port}")
    app.run(host, port, debug=False)



# ==============================
# Start Flask Server
# ==============================
if __name__ == '__main__':
    local_ip = get_local_ip()
    karmant()
    url = f"http://{host}:{port}"

    # ✅ Generate QR code
    qr_path = generate_qr_code(url)

    # ✅ Start Flask server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait a second to ensure server starts before opening browser
    time.sleep(1)

    # ✅ Open in browser
    open_browser(url)

    # ✅ Show menu
    show_menu(url, qr_path)


# pyinstaller --onefile --console v4.py