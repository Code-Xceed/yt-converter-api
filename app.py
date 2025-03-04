from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import threading
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # Enable CORS for all requests

# Define download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url, format="mp4", quality="best"):
    """Downloads YouTube video/audio using yt_dlp"""
    options = {
        'format': 'bestvideo+bestaudio/best' if format == "mp4" else 'bestaudio/best',
        'merge_output_format': format,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@app.route('/download', methods=['POST'])
def download():
    """API endpoint to download video/audio"""
    data = request.json
    url = data.get("url")
    format = data.get("format", "mp4")
    quality = data.get("quality", "best")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    threading.Thread(target=download_video, args=(url, format, quality)).start()
    return jsonify({"message": "Download started", "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
