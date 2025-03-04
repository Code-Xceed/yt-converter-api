import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS for frontend
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

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
        'user_agent': os.environ.get("YOUTUBE_USER_AGENT", ""),  # Use stored User-Agent
        'cookie': os.environ.get("YOUTUBE_COOKIES", ""),  # Use stored cookies
        'noprogress': True  # Removes unnecessary logs
    }

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

@app.route('/check-cookies')
def check_cookies():
    cookies_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
    return jsonify({"cookies_file_exists": os.path.exists(cookies_path)})

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
    app.run(host="0.0.0.0", port=10000)
