import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # Allow frontend access

# Define download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url, format="mp4"):
    """Downloads YouTube video/audio using yt-dlp with cookies from an environment variable"""

    options = {
        'format': 'bestvideo+bestaudio/best' if format == "mp4" else 'bestaudio/best',
        'merge_output_format': format,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': False,
        'noprogress': True,
    }

    # Get cookies from Render environment variable
    youtube_cookies = os.environ.get("YOUTUBE_COOKIES", None)
    youtube_user_agent = os.environ.get("YOUTUBE_USER_AGENT", None)

    if youtube_cookies:
        options["cookie"] = youtube_cookies

    if youtube_user_agent:
        options["user_agent"] = youtube_user_agent

    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return "YT Converter API is running!"

@app.route('/download', methods=['POST'])
def download():
    """API endpoint to download video/audio"""
    data = request.json
    url = data.get("url")
    format = data.get("format", "mp4")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        filename = download_video(url, format)
        return jsonify({"message": "Download started", "status": "success", "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

