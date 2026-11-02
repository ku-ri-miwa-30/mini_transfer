"""Step 1 のテスト。ミッションごとに `pytest -k m1` のように実行する。"""

import main


def upload(client, name="hello.txt", body=b"hello"):
    return client.post("/files", files={"file": (name, body, "application/octet-stream")})


# Mission 1 ------------------------------------------------------
def test_m1_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# Mission 2 ------------------------------------------------------
def test_m2_upload_returns_201_and_info(client):
    r = upload(client)
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "hello.txt", "size": 5}


def test_m2_ids_increase(client):
    upload(client, "a.txt", b"a")
    r = upload(client, "b.txt", b"bb")
    assert r.json()["id"] == 2


def test_m2_file_is_saved(client):
    upload(client, "hello.txt", b"hello")
    saved = list(main.STORAGE.iterdir())
    assert len(saved) == 1
    assert saved[0].read_bytes() == b"hello"


# Mission 3 ------------------------------------------------------
def test_m3_empty_list(client):
    r = client.get("/files")
    assert r.status_code == 200
    assert r.json() == []


def test_m3_list_after_uploads(client):
    upload(client, "a.txt", b"a")
    upload(client, "b.csv", b"x,y")
    r = client.get("/files")
    assert r.json() == [
        {"id": 1, "name": "a.txt", "size": 1},
        {"id": 2, "name": "b.csv", "size": 3},
    ]


# Mission 4 ------------------------------------------------------
def test_m4_download(client):
    upload(client, "hello.txt", b"hello")
    r = client.get("/files/1")
    assert r.status_code == 200
    assert r.content == b"hello"


def test_m4_download_not_found(client):
    r = client.get("/files/999")
    assert r.status_code == 404


# Mission 5 ------------------------------------------------------
def test_m5_delete(client):
    upload(client)
    r = client.delete("/files/1")
    assert r.status_code == 204
    assert client.get("/files").json() == []
    assert client.get("/files/1").status_code == 404
    assert list(main.STORAGE.iterdir()) == []


def test_m5_delete_not_found(client):
    r = client.delete("/files/999")
    assert r.status_code == 404


def test_m5_id_not_reused_after_delete(client):
    upload(client, "a.txt", b"a")
    upload(client, "b.txt", b"b")
    client.delete("/files/1")
    r = upload(client, "c.txt", b"c")
    assert r.json()["id"] == 3


# Mission 6 ------------------------------------------------------
def test_m6_reject_extension(client):
    r = upload(client, "virus.exe", b"MZ")
    assert r.status_code == 400
    assert client.get("/files").json() == []
    assert list(main.STORAGE.iterdir()) == []


def test_m6_reject_empty_file(client):
    r = upload(client, "empty.txt", b"")
    assert r.status_code == 400
    assert client.get("/files").json() == []


def test_m6_extension_is_case_insensitive(client):
    r = upload(client, "REPORT.PDF", b"%PDF")
    assert r.status_code == 201
