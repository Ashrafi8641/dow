
from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    format_type = data.get("format", "video")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = str(uuid.uuid4())
    ext = "mp4" if format_type == "video" else "mp3"
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.%(ext)s")

    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestaudio/best' if format_type == "audio" else 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4' if format_type == "video" else None,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }] if format_type == "audio" else [],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + f".{ext}"
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return open("index.html").read()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
