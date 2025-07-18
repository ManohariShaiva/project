from flask import Flask, request, render_template, send_from_directory
import os
from video_translator import process_local_video, process_youtube_video

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'final_outputs'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        lang_codes = request.form.getlist("languages")
        input_type = request.form.get("input_type")

        # Handle input type
        if input_type == "youtube":
            youtube_url = request.form.get("youtube_url")
            output_files = process_youtube_video(youtube_url, lang_codes)
        else:
            uploaded_file = request.files["video_file"]
            if uploaded_file.filename == "":
                return "No file selected"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            uploaded_file.save(filepath)
            output_files = process_local_video(filepath, lang_codes)

        outputs = {}
        for path in output_files:
            filename = os.path.basename(path)
            lang = os.path.splitext(filename)[0].split('_')[-1]
            ext = os.path.splitext(filename)[1].lower()

            if ext in ['.txt', '.srt', '.vtt']:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(path, 'r', encoding='latin1') as f:
                        content = f.read()
                outputs[lang] = {"type": "text", "content": content}
            elif ext in ['.mp4', '.webm', '.mov']:
                outputs[lang] = {"type": "video", "filename": filename}
            elif ext in ['.mp3', '.wav', '.ogg']:
                outputs[lang] = {"type": "audio", "filename": filename}
            else:
                outputs[lang] = {"type": "unknown", "filename": filename}

        return render_template("result.html", outputs=outputs)

    return render_template("index.html")


@app.route('/final_outputs/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(
        app.config['OUTPUT_FOLDER'],
        filename,
        as_attachment=False
    )


if __name__ == "__main__":
    app.run(debug=True)                                             







    



