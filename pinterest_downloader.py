"""
Pinterest Video Downloader
Install:  pip install flask yt-dlp
Run:      python pinterest_downloader.py
Open:     http://127.0.0.1:5000
"""
import os
import re
import shutil
import tempfile

import yt_dlp
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)

URL_RE = re.compile(
    r"^https://((\w+\.)?pinterest\.(com|co\.uk|de|fr|it|es|nl|se|ch|co\.in|br|au|at|cl|jp|ru|ie|ca|mx|nz|pt|ph)/.+|pin\.it/.+)$"
)

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pinterest Video Downloader</title>
<style>
  body{font-family:system-ui,sans-serif;background:#f5f5f5;margin:0;display:flex;
       min-height:100vh;align-items:center;justify-content:center}
  .card{background:#fff;padding:32px;border-radius:16px;width:min(560px,92vw);
        box-shadow:0 4px 24px rgba(0,0,0,.08)}
  h1{margin:0 0 16px;font-size:22px;color:#e60023}
  .row{display:flex;gap:8px}
  input{flex:1;padding:12px;font-size:16px;border:1px solid #ccc;border-radius:10px}
  button{padding:12px 20px;font-size:16px;border:0;border-radius:10px;
         background:#e60023;color:#fff;cursor:pointer}
  button:disabled{opacity:.6}
  .err{color:#b00020;margin-top:12px}
  .hint{color:#666;font-size:13px;margin-top:12px}
</style>
</head>
<body>
<div class="card">
  <h1>Pinterest Video Downloader</h1>
  <form method="POST" action="/download" onsubmit="b.disabled=true;b.textContent='Please wait...';
        setTimeout(()=>{b.disabled=false;b.textContent='Download'},8000)">
    <div class="row">
      <input name="url" placeholder="Enter Pinterest URL..." required autofocus
             pattern="https://.+" value="{{ url or '' }}">
      <button id="b" name="b">Download</button>
    </div>
  </form>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <div class="hint">Supports pinterest.com links and pin.it short links.</div>
</div>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/download")
def download():
    url = request.form.get("url", "").strip()
    if not URL_RE.match(url):
        return render_template_string(PAGE, error="Invalid Pinterest URL.", url=url), 400

    tmp = tempfile.mkdtemp()
    opts = {
        "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
        "format": "best",
        "noplaylist": True,
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
        with open(path, "rb") as f:
            data = f.read()
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        msg = "Could not download. Make sure the pin contains a video and is public."
        return render_template_string(PAGE, error=f"{msg} ({str(e)[:120]})", url=url), 400

    shutil.rmtree(tmp, ignore_errors=True)
    from io import BytesIO
    return send_file(
        BytesIO(data),
        as_attachment=True,
        download_name=os.path.basename(path),
        mimetype="video/mp4",
    )


if __name__ == "__main__":
    app.run(debug=False)
