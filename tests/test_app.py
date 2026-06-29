import pytest
import json
from app import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "DATA_FILE", tmp_path / "todos.json")
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_index_empty(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Ingen oppgaver" in r.data.decode()


def test_add_todo(client):
    r = client.post("/add", data={"text": "Handle mat"}, follow_redirects=True)
    assert r.status_code == 200
    assert "Handle mat" in r.data.decode()


def test_add_empty_todo_ignored(client):
    client.post("/add", data={"text": ""}, follow_redirects=True)
    r = client.get("/")
    assert "Ingen oppgaver" in r.data.decode()


def test_done_toggle(client):
    client.post("/add", data={"text": "Gjør dette"}, follow_redirects=True)
    r = client.post("/done/1", follow_redirects=True)
    assert r.status_code == 200
    assert "done" in r.data.decode()


def test_delete_todo(client):
    client.post("/add", data={"text": "Slett meg"}, follow_redirects=True)
    r = client.post("/delete/1", follow_redirects=True)
    assert r.status_code == 200
    assert "Ingen oppgaver" in r.data.decode()


def test_stats_shown(client):
    client.post("/add", data={"text": "Oppgave 1"}, follow_redirects=True)
    client.post("/add", data={"text": "Oppgave 2"}, follow_redirects=True)
    client.post("/done/1", follow_redirects=True)
    r = client.get("/")
    assert "1 av 2" in r.data.decode()
