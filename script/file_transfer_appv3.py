import os
import io
import base64
import socket
import threading
import webbrowser
from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import qrcode
import platform
import subprocess

# ==============================
# Use current directory for uploads
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================
# Flask app
# ==============================
app = Flask(__name__)

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

def generate_qr_base64(link):
    img = qrcode.make(link)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def open_directory(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass

# ==============================
# HTML Template
# ==============================
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>📁 File Transfer</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family: Arial,sans-serif; background:#f8fafc; color:#1e293b; margin:0; padding:20px; display:flex; flex-direction:column; align-items:center;}
.container { max-width:600px; width:100%; }
.card { background:#fff; padding:20px; border-radius:12px; margin-bottom:20px; box-shadow:0 4px 6px rgba(0,0,0,0.1); }
h2 { margin-top:0; }
ul { list-style:none; padding:0; }
li { padding:10px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; }
button { padding:10px 16px; border:none; background:#6366f1; color:white; border-radius:8px; cursor:pointer; font-weight:600; }
a { text-decoration:none; color:#6366f1; }
input[type="file"] { width:100%; margin-bottom:12px; }
progress { width:100%; height:10px; border-radius:10px; overflow:hidden; border:none; display:none; }
</style>
</head>
<body>
<div class="container">
    <div class="card">
        <h2>📱 Phone Access</h2>
        <img src="data:image/png;base64,{{ qr_code_img }}" width="180">
        <p>Link: <a href="{{ url }}">{{ url }}</a></p>
    </div>

    <div class="card">
        <h2>📁 Current Directory Files</h2>
        <form method="POST" action="/open_directory"><button type="submit">📂 Open Directory</button></form>
        {% if files %}
        <ul>
            {% for file in files %}
            <li>
                <span>{{ file }}</span>
                <a href="/download/{{ file }}">Download</a>
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No files yet.</p>
        {% endif %}
        <form method="POST" action="/shutdown"><button type="submit" style="background:#ef4444">❌ Stop Server</button></form>
    </div>

    <div class="card">
        <h2>📤 Upload Files</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="files" id="fileInput" multiple required>
            <button type="submit">Upload</button>
        </form>
        <progress id="uploadProgress" max="100"></progress>
        <p id="statusText"></p>
    </div>
</div>

<script>
document.getElementById('uploadForm').addEventListener('submit', function(e){
    e.preventDefault();
    const files = document.getElementById('fileInput').files;
    if (!files.length) return;

    const formData = new FormData();
    for(let i=0;i<files.length;i++){ formData.append("files", files[i]); }

    const xhr = new XMLHttpRequest();
    xhr.open("POST","/upload",true);
    const progressBar = document.getElementById('uploadProgress');
    const statusText = document.getElementById('statusText');
    progressBar.style.display = 'block';

    xhr.upload.onprogress = function(e){
        if(e.lengthComputable){
            progressBar.value = (e.loaded/e.total)*100;
            statusText.innerText = `Uploading: ${Math.round((e.loaded/e.total)*100)}%`;
        }
    };
    xhr.onload = function(){
        if(xhr.status===200){ statusText.innerText="✅ Done! Refreshing..."; setTimeout(()=>location.reload(),1000); }
        else{ statusText.innerText="❌ Upload failed"; }
    };
    xhr.onerror=function(){ statusText.innerText="❌ Network error"; };
    xhr.send(formData);
});
</script>
</body>
</html>
'''

# ==============================
# Routes
# ==============================
@app.route("/")
def index():
    url = f"http://{get_local_ip()}:8000"
    qr_code_img = generate_qr_base64(url)
    files = [f for f in os.listdir(FTP_FOLDER) if os.path.isfile(os.path.join(FTP_FOLDER, f))]
    return render_template_string(html_template, qr_code_img=qr_code_img, url=url, files=files)


# Flask upload route
@app.route('/upload', methods=['POST'])
def upload():
    for file in request.files.getlist('files'):
        if file.filename:
            file.save(os.path.join(FTP_FOLDER, secure_filename(file.filename)))
    return '', 200

# Download route
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(FTP_FOLDER, filename, as_attachment=True)

# Open directory button
@app.route('/open_directory', methods=['POST'])
def open_dir():
    open_directory(FTP_FOLDER)
    return redirect(url_for('index'))


# ==============================
# Run server
# ==============================
def run():
    ip = get_local_ip()
    url = f"http://{ip}:8000"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=8000, debug=False)

if __name__ == "__main__":
    run()