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


def test_new_post_page_renders_create_mode_form(client):
    response = client.get("/posts/new")

    assert response.status_code == 200
    assert b"Structured Editor" in response.data
    assert b'class="write-form"' in response.data
    assert b'action="/posts"' in response.data
    assert b"Publish" in response.data
    assert b"Update" not in response.data


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


def test_edit_page_renders_existing_post_in_edit_mode_form(client, app):
    post_id = _seed_post(app, title="Before Edit", content="Before Body")

    response = client.get(f"/posts/{post_id}/edit")

    assert response.status_code == 200
    assert b"Structured Editor" in response.data
    assert b'class="write-form"' in response.data
    assert f'action="/posts/{post_id}/edit"'.encode() in response.data
    assert b"Before Edit" in response.data
    assert b"Before Body" in response.data
    assert b"Update" in response.data
    assert b"Publish" not in response.data


def test_edit_post_updates_and_redirects(client, app):
    post_id = _seed_post(app, title="Old Title", content="Old Content")

    response = client.post(
        f"/posts/{post_id}/edit",
        data={"title": "New Title", "content": "New Content"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == f"/posts/{post_id}"

    detail = client.get(f"/posts/{post_id}")
    assert b"New Title" in detail.data
    assert b"New Content" in detail.data


def test_edit_post_rejects_whitespace_only_fields(client, app):
    post_id = _seed_post(app, title="Original Title", content="Original Content")

    response = client.post(
        f"/posts/{post_id}/edit",
        data={"title": "   ", "content": "   "},
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert "제목과 본문을 입력해주세요.".encode("utf-8") in response.data


def test_edit_post_invalid_input_does_not_change_stored_post(client, app):
    post_id = _seed_post(app, title="Original Title", content="Original Content")

    response = client.post(
        f"/posts/{post_id}/edit",
        data={"title": "   ", "content": "   "},
        follow_redirects=False,
    )

    assert response.status_code == 400

    with app.app_context():
        from app import get_db

        row = get_db().execute(
            "SELECT title, content FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()

    assert row["title"] == "Original Title"
    assert row["content"] == "Original Content"


def test_delete_post_removes_record_and_redirects(client, app):
    post_id = _seed_post(app, title="Delete Me", content="Delete Body")

    response = client.post(f"/posts/{post_id}/delete", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    detail = client.get(f"/posts/{post_id}")
    assert detail.status_code == 404


def test_delete_missing_post_returns_404(client):
    response = client.post("/posts/999999/delete")
    assert response.status_code == 404


def test_list_page_has_start_writing_cta(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Start Writing" in response.data


def test_write_form_has_editor_heading(client):
    response = client.get("/posts/new")
    assert response.status_code == 200
    assert b"Structured Editor" in response.data
