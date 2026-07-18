#!/usr/bin/env python3
import json
import sys
from pathlib import Path

DATA_FILE = Path("todos.json")


def load_todos():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []


def save_todos(todos):
    DATA_FILE.write_text(json.dumps(todos, indent=2, ensure_ascii=False))


def add_todo(text):
    todos = load_todos()
    todos.append({"id": len(todos) + 1, "text": text, "done": False})
    save_todos(todos)
    print(f"Lagt til: {text}")


def list_todos():
    todos = load_todos()
    if not todos:
        print("Ingen oppgaver ennå. Legg til med: python todo.py add <oppgave>")
        return
    for todo in todos:
        status = "✓" if todo["done"] else "○"
        print(f"  [{status}] {todo['id']}. {todo['text']}")


def done_todo(todo_id):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            save_todos(todos)
            print(f"Ferdig: {todo['text']}")
            return
    print(f"Fant ingen oppgave med id {todo_id}")


def delete_todo(todo_id):
    todos = load_todos()
    original_len = len(todos)
    todos = [t for t in todos if t["id"] != todo_id]
    if len(todos) == original_len:
        print(f"Fant ingen oppgave med id {todo_id}")
        return
    save_todos(todos)
    print(f"Slettet oppgave {todo_id}")


def print_help():
    print("Bruk:")
    print("  python todo.py add <oppgave>   Legg til en oppgave")
    print("  python todo.py list            Vis alle oppgaver")
    print("  python todo.py done <id>       Merk oppgave som ferdig")
    print("  python todo.py delete <id>     Slett en oppgave")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Feil: Mangler oppgavetekst")
            sys.exit(1)
        add_todo(" ".join(sys.argv[2:]))

    elif command == "list":
        list_todos()

    elif command == "done":
        if len(sys.argv) < 3:
            print("Feil: Mangler id")
            sys.exit(1)
        done_todo(int(sys.argv[2]))

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Feil: Mangler id")
            sys.exit(1)
        delete_todo(int(sys.argv[2]))

    else:
        print(f"Ukjent kommando: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
