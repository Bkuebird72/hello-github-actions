import json
import pytest
from pathlib import Path
from unittest.mock import patch

import todo


@pytest.fixture(autouse=True)
def temp_data_file(tmp_path, monkeypatch):
    data_file = tmp_path / "todos.json"
    monkeypatch.setattr(todo, "DATA_FILE", data_file)
    return data_file


def test_load_todos_returns_empty_list_when_no_file():
    result = todo.load_todos()
    assert result == []


def test_add_todo(capsys):
    todo.add_todo("Handle inn mat")
    captured = capsys.readouterr()
    assert "Handle inn mat" in captured.out

    todos = todo.load_todos()
    assert len(todos) == 1
    assert todos[0]["text"] == "Handle inn mat"
    assert todos[0]["done"] is False
    assert todos[0]["id"] == 1


def test_add_multiple_todos():
    todo.add_todo("Første oppgave")
    todo.add_todo("Andre oppgave")
    todo.add_todo("Tredje oppgave")

    todos = todo.load_todos()
    assert len(todos) == 3
    assert todos[0]["id"] == 1
    assert todos[1]["id"] == 2
    assert todos[2]["id"] == 3


def test_list_todos_empty(capsys):
    todo.list_todos()
    captured = capsys.readouterr()
    assert "Ingen oppgaver" in captured.out


def test_list_todos(capsys):
    todo.add_todo("Første oppgave")
    todo.add_todo("Andre oppgave")
    todo.list_todos()
    captured = capsys.readouterr()
    assert "Første oppgave" in captured.out
    assert "Andre oppgave" in captured.out


def test_done_todo(capsys):
    todo.add_todo("Gjør noe")
    todo.done_todo(1)

    todos = todo.load_todos()
    assert todos[0]["done"] is True

    captured = capsys.readouterr()
    assert "Ferdig" in captured.out


def test_done_todo_nonexistent(capsys):
    todo.done_todo(999)
    captured = capsys.readouterr()
    assert "Fant ingen" in captured.out


def test_delete_todo(capsys):
    todo.add_todo("Slett meg")
    todo.delete_todo(1)

    todos = todo.load_todos()
    assert len(todos) == 0

    captured = capsys.readouterr()
    assert "Slettet" in captured.out


def test_delete_todo_nonexistent(capsys):
    todo.delete_todo(999)
    captured = capsys.readouterr()
    assert "Fant ingen" in captured.out


def test_list_shows_done_status(capsys):
    todo.add_todo("Ferdig oppgave")
    todo.done_todo(1)
    todo.list_todos()
    captured = capsys.readouterr()
    assert "✓" in captured.out
