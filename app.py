from urllib.parse import quote  # Doğru modül

from flask import Flask, render_template, request, Response
import yt_dlp
import requests
import instaloader
import os
app = Flask(__name__)

# Instaloader nesnesi oluştur
L = instaloader.Instaloader()

# Giriş yapmayı dene (session dosyasını kullan)
SESSION_FILE = "session-127373772vbx"

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



if os.path.exists(SESSION_FILE):
    try:
        L.load_session_from_file("YOUR_USERNAME")
        print("✅ Instagram oturumu başarıyla yüklendi!")
    except Exception as e:
        print(f"❌ Oturum yükleme hatası: {e}")
else:
    print("⚠️ Oturum dosyası bulunamadı. Önce terminalde giriş yapmalısın!")

@app.route("/instagram", methods=["GET", "POST"])
def instagram():
    if request.method == "POST":
        url = request.form.get("url")

        try:
            # URL'den shortcode'u al (örn: https://www.instagram.com/reel/XYZ123/ -> XYZ123)
            shortcode = url.split("/")[-2]

            # Instaloader ile gönderi bilgilerini al
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            # Video URL'sini al
            if post.is_video:
                video_url = post.video_url
                return render_template("stream.html", stream_url=video_url, platform="Instagram", title="Instagram Video")
            else:
                return render_template("instagram.html", error="Bu gönderi bir video içermiyor.")

        except Exception as e:
            return render_template("instagram.html", error=f"Hata: {e}")

    return render_template("instagram.html")

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
