
import os
from pathlib import Path
from html import escape

from flask import Flask, abort, send_from_directory, url_for

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Render persistent storage directory.
# If FILES_DIR is not configured, use the local files folder.
FILES_DIR = Path(os.environ.get("FILES_DIR", BASE_DIR / "files"))

FILES_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 30 * 1024 * 1024


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return "OK", 200


@app.route("/file-list")
def file_list():

    rows = []

    for file in sorted(FILES_DIR.iterdir(), key=lambda p: p.name.lower()):

        if file.is_symlink() or not file.is_file():
            continue

        try:
            size = file.stat().st_size
        except OSError:
            continue

        # Maximum size: 30 MB
        if size > MAX_FILE_SIZE:
            continue

        size_mb = size / (1024 * 1024)

        safe_name = escape(file.name)

        download_url = url_for(
            "download_file",
            filename=file.name
        )

        rows.append(
            "<tr>"
            f"<td>{safe_name}</td>"
            f"<td>{size_mb:.2f} MB</td>"
            f'<td><a href="{escape(download_url, quote=True)}" target="_top">'
            '<button type="button">Download</button></a></td>'
            "</tr>"
        )

    if not rows:
        content = """
        <tr>
            <td colspan="3">No downloadable files available.</td>
        </tr>
        """
    else:
        content = "".join(rows)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Available Files</title>
    </head>

    <body>

        <table>
            <thead>
                <tr>
                    <th align="left">File Name</th>
                    <th align="left">Size</th>
                    <th align="left">Action</th>
                </tr>
            </thead>

            <tbody>
                {content}
            </tbody>
        </table>

    </body>
    </html>
    """


@app.route("/download/<path:filename>")
def download_file(filename):

    file_path = FILES_DIR / filename

    if file_path.is_symlink() or not file_path.is_file():
        abort(404)

    if file_path.stat().st_size > MAX_FILE_SIZE:
        abort(403)

    return send_from_directory(
        FILES_DIR,
        filename,
        as_attachment=True,
        download_name=file_path.name
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
