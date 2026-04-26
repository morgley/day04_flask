import re
import sqlite3
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlparse


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


def _extract_post_titles(html):
    return re.findall(
        r'<article class="post-item">.*?<h2><a[^>]*>(.*?)</a></h2>',
        html,
        flags=re.S,
    )


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


def test_list_page_shows_only_ten_posts_per_page(client, app):
    for i in range(1, 26):
        _seed_post(app, title=f"Page Title {i}", content=f"Page Body {i}")

    response = client.get("/?page=1")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert len(re.findall(r'class="[^"]*\bpost-item\b[^"]*"', html)) == 10
    assert "Page Title 25" in html
    assert "Page Title 16" in html
    assert "Page Title 15" not in html


def test_list_page_clamps_invalid_page_values_to_first_page(client, app):
    for i in range(1, 26):
        _seed_post(app, title=f"Clamp Title {i}", content=f"Clamp Body {i}")

    for value in ["0", "-1", "abc"]:
        response = client.get(f"/?page={value}")
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert len(re.findall(r'class="[^"]*\bpost-item\b[^"]*"', html)) == 10
        assert "Clamp Title 25" in html
        assert "Clamp Title 16" in html
        assert "Clamp Title 15" not in html


def test_list_page_clamps_large_page_to_last_page(client, app):
    for i in range(1, 26):
        _seed_post(app, title=f"Last Title {i}", content=f"Last Body {i}")

    response = client.get("/?page=999")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert len(re.findall(r'class="[^"]*\bpost-item\b[^"]*"', html)) == 5
    assert "Last Title 5" in html
    assert "Last Title 1" in html
    assert "Last Title 6" not in html


def test_first_page_shows_indicator_and_disables_previous(client, app):
    for i in range(1, 26):
        _seed_post(app, title=f"Nav Title {i}", content=f"Nav Body {i}")

    response = client.get("/?page=1")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "1 / 3" in html
    assert re.search(
        r'<span[^>]*class="[^"]*pager-link[^"]*is-disabled[^"]*"[^>]*>\s*\[이전\]\s*</span>',
        html,
    )
    next_href = re.search(r'<a[^>]*href="([^"]+)"[^>]*>\s*\[다음\]\s*</a>', html)
    assert next_href is not None
    next_query = parse_qs(urlparse(unescape(next_href.group(1))).query)
    assert next_query.get("page") == ["2"]
    assert not re.search(r'<a[^>]*href="/\?page=0"[^>]*>\s*\[이전\]\s*</a>', html)


def test_last_page_disables_next(client, app):
    for i in range(1, 26):
        _seed_post(app, title=f"Nav Last Title {i}", content=f"Nav Last Body {i}")

    response = client.get("/?page=3")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "3 / 3" in html
    prev_href = re.search(r'<a[^>]*href="([^"]+)"[^>]*>\s*\[이전\]\s*</a>', html)
    assert prev_href is not None
    prev_query = parse_qs(urlparse(unescape(prev_href.group(1))).query)
    assert prev_query.get("page") == ["2"]
    assert re.search(
        r'<span[^>]*class="[^"]*pager-link[^"]*is-disabled[^"]*"[^>]*>\s*\[다음\]\s*</span>',
        html,
    )
    assert not re.search(r'<a[^>]*href="/\?page=4"[^>]*>\s*\[다음\]\s*</a>', html)


def test_search_filters_posts_by_title_or_content(client, app):
    _seed_post(app, title="Flask Guide", content="Routing basics")
    _seed_post(app, title="Database Notes", content="SQLite optimization")
    _seed_post(app, title="Testing", content="Flask client patterns")

    response = client.get("/?q=flask")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Flask Guide" in html
    assert "Testing" in html
    assert "Database Notes" not in html


def test_search_shows_empty_message_when_no_results(client, app):
    _seed_post(app, title="Alpha", content="First")

    response = client.get("/?q=zzzz-no-hit")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "검색 결과가 없습니다" in html
    assert len(re.findall(r'class="[^"]*\bpost-item\b[^"]*"', html)) == 0
    assert "Alpha" not in html


def test_sort_oldest_orders_posts_ascending_by_id(client, app):
    _seed_post(app, title="Oldest", content="a")
    _seed_post(app, title="Middle", content="b")
    _seed_post(app, title="Newest", content="c")

    response = client.get("/?sort=oldest")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    titles = _extract_post_titles(html)
    assert titles[:3] == ["Oldest", "Middle", "Newest"]


def test_sort_title_orders_posts_by_title_case_insensitive(client, app):
    _seed_post(app, title="banana", content="1")
    _seed_post(app, title="Apple", content="2")
    _seed_post(app, title="cherry", content="3")

    response = client.get("/?sort=title")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    titles = _extract_post_titles(html)
    assert titles[:3] == ["Apple", "banana", "cherry"]


def test_invalid_sort_falls_back_to_latest(client, app):
    _seed_post(app, title="First", content="1")
    _seed_post(app, title="Second", content="2")

    response = client.get("/?sort=invalid-value")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    titles = _extract_post_titles(html)
    assert titles[:2] == ["Second", "First"]


def test_combined_search_sort_and_pagination_keeps_ten_per_page(client, app):
    for i in range(1, 21):
        _seed_post(app, title=f"Flask Post {i:02d}", content="hit")
    _seed_post(app, title="Other Topic", content="miss")

    response = client.get("/?q=flask&sort=oldest&page=2")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert len(re.findall(r'class="[^"]*\bpost-item\b[^"]*"', html)) == 10
    titles = _extract_post_titles(html)
    assert titles == [
        "Flask Post 11",
        "Flask Post 12",
        "Flask Post 13",
        "Flask Post 14",
        "Flask Post 15",
        "Flask Post 16",
        "Flask Post 17",
        "Flask Post 18",
        "Flask Post 19",
        "Flask Post 20",
    ]
    assert "Other Topic" not in html


def test_pager_links_keep_q_and_sort(client, app):
    for i in range(1, 21):
        _seed_post(app, title=f"Flask {i:02d}", content="hit")

    response = client.get("/?q=flask&sort=title&page=1")
    html = response.get_data(as_text=True)

    assert response.status_code == 200

    next_href = re.search(r'<a[^>]*href="([^"]+)"[^>]*>\s*\[다음\]\s*</a>', html)
    assert next_href is not None

    next_query = parse_qs(urlparse(unescape(next_href.group(1))).query)
    assert next_query == {"q": ["flask"], "sort": ["title"], "page": ["2"]}


def test_sort_change_form_resets_page_to_one(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert re.search(r'name=["\']page["\']\s+value=["\']1["\']', html)


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


def test_database_path_resolves_inside_project_dir():
    from app import create_app

    app = create_app()

    expected = (Path(__file__).resolve().parents[1] / "instance" / "board.db").resolve()
    assert Path(app.config["DATABASE"]).resolve() == expected


def test_database_path_is_stable_even_when_import_name_is_main(monkeypatch, tmp_path):
    import app as app_module

    monkeypatch.chdir(tmp_path)
    original_name = app_module.__name__
    try:
        app_module.__name__ = "__main__"
        app = app_module.create_app()
    finally:
        app_module.__name__ = original_name

    expected = (Path(__file__).resolve().parents[1] / "instance" / "board.db").resolve()
    assert Path(app.config["DATABASE"]).resolve() == expected
