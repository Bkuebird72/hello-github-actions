from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path("todos.json")


def load_todos():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save_todos(todos):
    DATA_FILE.write_text(json.dumps(todos, indent=2, ensure_ascii=False))


def next_id(todos):
    return max((t["id"] for t in todos), default=0) + 1


@app.route("/")
def index():
    todos = load_todos()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text", "").strip()
    if text:
        todos = load_todos()
        todos.append({"id": next_id(todos), "text": text, "done": False})
        save_todos(todos)
    return redirect(url_for("index"))


@app.route("/done/<int:todo_id>", methods=["POST"])
def done(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            break
    save_todos(todos)
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
