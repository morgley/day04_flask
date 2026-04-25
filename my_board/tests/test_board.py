import sqlite3
from datetime import datetime


def _seed_post(app, title="First", content="Body"):
    with app.app_context():
        from app import get_db, init_db

        init_db()
        db = get_db()
        db.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        db.commit()
        return db.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1").fetchone()["id"]


def test_index_health(client):
    response = client.get("/")
    assert response.status_code == 200


def test_init_db_creates_posts_table(app):
    db_path = app.config["DATABASE"]

    with app.app_context():
        from app import init_db

        init_db()

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='posts'"
        ).fetchone()
    finally:
        conn.close()

    assert row is not None


def test_list_page_shows_posts(client, app):
    _seed_post(app, title="List Title", content="List Content")

    response = client.get("/")

    assert response.status_code == 200
    assert b"List Title" in response.data


def test_detail_page_shows_post_content(client, app):
    post_id = _seed_post(app, title="Detail Title", content="Detail Content")

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert b"Detail Title" in response.data
    assert b"Detail Content" in response.data


def test_detail_page_returns_404_for_missing_post(client):
    response = client.get("/posts/999999")

    assert response.status_code == 404


def test_new_post_page_renders(client):
    response = client.get("/posts/new")

    assert response.status_code == 200
    assert b"Write" in response.data


def test_create_post_redirects_to_detail(client):
    response = client.post(
        "/posts",
        data={"title": "Created Title", "content": "Created Content"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/posts/")


def test_create_post_rejects_blank_fields(client):
    response = client.post(
        "/posts",
        data={"title": "", "content": ""},
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert "제목과 본문을 입력해주세요.".encode("utf-8") in response.data
