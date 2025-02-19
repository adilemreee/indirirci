from urllib.parse import quote
from flask import Flask, render_template, request, Response
import yt_dlp
import requests

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/youtube", methods=["GET", "POST"])
def youtube():
    if request.method == "POST":
        url = request.form.get("url")
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'noplaylist': True,
                'nocache': True,
                'cachedir': False,  # Önbelleği tamamen kapat
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                stream_url = info_dict.get('url', None)
                title = info_dict.get('title', 'video')

                if stream_url:
                    return render_template("stream.html", stream_url=stream_url, platform="YouTube", title=title)
                else:
                    raise ValueError("Could not retrieve stream URL.")

        except Exception as e:
            print(f"Error: {e}")
            error_message = f"Error: {e}"
            return render_template("youtube.html", error=error_message)

    return render_template("youtube.html")


@app.route("/download")
def download():
    video_url = request.args.get("url")
    filename = request.args.get("filename", "video.mp4")

    safe_filename = quote(filename)

    if not video_url:
        return "Invalid video URL", 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Bazı videolar için gerekli olabilir
        response = requests.get(video_url, stream=True, headers=headers)

        return Response(
            response.iter_content(chunk_size=1024),
            content_type=response.headers["Content-Type"],
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"}
        )

    except Exception as e:
        print(f"Download Error: {e}")
        return "Error while downloading", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)