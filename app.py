
from flask import Flask, send_from_directory, abort, render_template_string
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

FILES_DIR.mkdir(exist_ok=True)

MAX_SIZE = 30 * 1024 * 1024


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/file-list")
def file_list():

    rows = []

    for file in sorted(FILES_DIR.iterdir()):

        if not file.is_file():
            continue

        if file.stat().st_size > MAX_SIZE:
            continue

        size = file.stat().st_size / (1024 * 1024)

        rows.append(f"""
            <tr>
                <td>{file.name}</td>
                <td>{size:.2f} MB</td>
                <td>
                    <a href="/download/{file.name.replace('&', '%26').replace('#', '%23')}"
                       target="_top">
                       <button>Download</button>
                    </a>
                </td>
            </tr>
        """)

    if not rows:
        content = "<p>No available files.</p>"
    else:
        content = "<table>" + "".join(rows) + "</table>"

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <body>
            {{ content | safe }}
        </body>
        </html>
    """, content=content)


@app.route("/download/<path:filename>")
def download(filename):

    file_path = (FILES_DIR / filename).resolve()

    if not file_path.is_relative_to(FILES_DIR.resolve()):
        abort(404)

    if not file_path.is_file():
        abort(404)

    if file_path.stat().st_size > MAX_SIZE:
        abort(403)

    return send_from_directory(
        FILES_DIR,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
