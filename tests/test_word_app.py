import pytest
from urllib.parse import urlparse
import word_app
from word_app import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(word_app, "DOCS_DIR", tmp_path)
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _new_doc(client):
    r = client.post("/new", follow_redirects=False)
    return urlparse(r.location).path.split("/")[-1]


def test_index_empty(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Ingen dokumenter" in r.data.decode()


def test_new_doc_redirects_to_editor(client):
    r = client.post("/new", follow_redirects=True)
    assert r.status_code == 200
    assert "Nytt dokument" in r.data.decode()


def test_index_shows_document_after_creation(client):
    _new_doc(client)
    r = client.get("/")
    assert "Nytt dokument" in r.data.decode()


def test_save_doc(client):
    doc_id = _new_doc(client)
    r = client.post(f"/save/{doc_id}", json={
        "title": "Min rapport",
        "content": "<p>Hei verden</p>",
        "words": 2
    })
    assert r.json["ok"] is True
    assert "modified" in r.json


def test_saved_title_appears_in_index(client):
    doc_id = _new_doc(client)
    client.post(f"/save/{doc_id}", json={"title": "Årsrapport", "content": "", "words": 0})
    r = client.get("/")
    assert "Årsrapport" in r.data.decode()


def test_saved_content_loads_in_editor(client):
    doc_id = _new_doc(client)
    client.post(f"/save/{doc_id}", json={
        "title": "Test", "content": "<p>Innhold her</p>", "words": 2
    })
    r = client.get(f"/edit/{doc_id}")
    assert "Innhold her" in r.data.decode()


def test_delete_doc(client):
    doc_id = _new_doc(client)
    r = client.post(f"/delete/{doc_id}", follow_redirects=True)
    assert r.status_code == 200
    assert "Ingen dokumenter" in r.data.decode()


def test_export_doc(client):
    doc_id = _new_doc(client)
    client.post(f"/save/{doc_id}", json={
        "title": "Eksport test", "content": "<p>Tekst her</p>", "words": 2
    })
    r = client.get(f"/export/{doc_id}")
    assert r.status_code == 200
    assert b"Eksport test" in r.data
    assert b"Tekst her" in r.data


def test_edit_nonexistent_doc_redirects(client):
    r = client.get("/edit/nonexistent", follow_redirects=True)
    assert r.status_code == 200


def test_multiple_docs_listed(client):
    d1 = _new_doc(client)
    d2 = _new_doc(client)
    client.post(f"/save/{d1}", json={"title": "Dok 1", "content": "", "words": 0})
    client.post(f"/save/{d2}", json={"title": "Dok 2", "content": "", "words": 0})
    r = client.get("/")
    body = r.data.decode()
    assert "Dok 1" in body and "Dok 2" in body
