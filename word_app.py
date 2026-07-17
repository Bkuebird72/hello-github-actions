from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import json
import uuid
from pathlib import Path
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
DOCS_DIR = Path("documents")
DOCS_DIR.mkdir(exist_ok=True)


def _path(doc_id):
    return DOCS_DIR / f"{doc_id}.json"


def _load(doc_id):
    p = _path(doc_id)
    return json.loads(p.read_text()) if p.exists() else None


def _persist(doc_id, doc):
    _path(doc_id).write_text(json.dumps(doc, indent=2, ensure_ascii=False))


def _list():
    docs = []
    for f in sorted(DOCS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            docs.append(json.loads(f.read_text()))
        except Exception:
            pass
    return docs


def _now():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def _to_html(title, content):
    return f"""<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body{{font-family:Calibri,'Segoe UI',sans-serif;max-width:21cm;margin:2cm auto;
         padding:0 2cm;font-size:11pt;line-height:1.5;color:#111}}
    h1{{font-size:20pt;border-bottom:1px solid #ddd;padding-bottom:.3em}}
    h2{{font-size:16pt}}h3{{font-size:13pt}}p{{margin:.3em 0}}
  </style>
</head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>"""


@app.route("/")
def index():
    return render_template("word_index.html", docs=_list())


@app.route("/new", methods=["POST"])
def new_doc():
    doc_id = uuid.uuid4().hex[:8]
    now = _now()
    doc = {"id": doc_id, "title": "Nytt dokument", "content": "",
           "created": now, "modified": now, "words": 0}
    _persist(doc_id, doc)
    return redirect(url_for("editor", doc_id=doc_id))


@app.route("/edit/<doc_id>")
def editor(doc_id):
    doc = _load(doc_id)
    if not doc:
        return redirect(url_for("index"))
    return render_template("word_editor.html", doc=doc)


@app.route("/save/<doc_id>", methods=["POST"])
def save(doc_id):
    existing = _load(doc_id) or {"id": doc_id, "created": _now()}
    data = request.get_json(force=True)
    existing.update({
        "title": data.get("title", "Nytt dokument"),
        "content": data.get("content", ""),
        "words": int(data.get("words", 0)),
        "modified": _now(),
    })
    _persist(doc_id, existing)
    return jsonify({"ok": True, "modified": existing["modified"]})


@app.route("/delete/<doc_id>", methods=["POST"])
def delete_doc(doc_id):
    p = _path(doc_id)
    if p.exists():
        p.unlink()
    return redirect(url_for("index"))


@app.route("/export/<doc_id>")
def export_doc(doc_id):
    doc = _load(doc_id)
    if not doc:
        return redirect(url_for("index"))
    html = _to_html(doc["title"], doc["content"])
    return send_file(
        BytesIO(html.encode("utf-8")),
        mimetype="text/html",
        as_attachment=True,
        download_name=f"{doc['title']}.html",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
