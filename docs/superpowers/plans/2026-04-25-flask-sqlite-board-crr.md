# Flask SQLite Board (C/R/R) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Flask + SQLite board app at `my-board/my_board` with create, list, and detail features using the provided design references.

**Architecture:** Use a single-file Flask app (`app.py`) with Jinja templates and direct SQLite access via `sqlite3`. Keep a shared `base.html` for Linen & Logic common layout/theme and three page templates for list/detail/write. Store data in `instance/board.db` with a bootstrap schema initializer.

**Tech Stack:** Python 3 (Ubuntu 24.04), Flask, sqlite3, Jinja2, pytest

---

## File Structure

- Create: `my-board/my_board/app.py` — Flask app factory, DB helpers, routes (`/`, `/posts/new`, `/posts`, `/posts/<id>`), schema init.
- Create: `my-board/my_board/requirements.txt` — Flask + test dependency pins.
- Create: `my-board/my_board/templates/base.html` — common Linen & Logic header/theme wrapper.
- Create: `my-board/my_board/templates/post_list.html` — list page based on `post_list_minimalist_text`.
- Create: `my-board/my_board/templates/post_detail.html` — detail page based on `post_detail` (without edit/delete actions).
- Create: `my-board/my_board/templates/post_form.html` — write page based on `write_post_sidebar_editor` simplified to title/content form.
- Create: `my-board/my_board/static/style.css` — shared warm minimalist styles and layout overrides.
- Create: `my-board/my_board/tests/conftest.py` — app/test client fixtures with temp SQLite DB.
- Create: `my-board/my_board/tests/test_board.py` — TDD coverage for schema, create, list, detail.
- Create: `my-board/my_board/.gitignore` — ignore `.venv`, `instance`, caches.

### Task 1: Scaffold project and test harness

**Files:**
- Create: `my-board/my_board/.gitignore`
- Create: `my-board/my_board/requirements.txt`
- Create: `my-board/my_board/app.py`
- Create: `my-board/my_board/tests/conftest.py`
- Create: `my-board/my_board/tests/test_board.py`

- [ ] **Step 1: Create baseline project files**

```gitignore
# my-board/my_board/.gitignore
.venv/
__pycache__/
.pytest_cache/
instance/
```

```text
# my-board/my_board/requirements.txt
Flask==3.0.3
pytest==8.3.2
```

```python
# my-board/my_board/app.py
from __future__ import annotations

from flask import Flask


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE="instance/board.db",
    )

    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return "ok"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

```python
# my-board/my_board/tests/conftest.py
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def app():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        app = create_app({"TESTING": True, "DATABASE": str(db_path)})
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()
```

```python
# my-board/my_board/tests/test_board.py
def test_index_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ok" in response.data
```

- [ ] **Step 2: Create venv and install dependencies**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
Expected: pip installs Flask and pytest successfully.

- [ ] **Step 3: Run baseline test**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest -v`
Expected: PASS for `test_index_health`.

- [ ] **Step 4: Commit scaffold**

```bash
git add my-board/my_board/.gitignore my-board/my_board/requirements.txt my-board/my_board/app.py my-board/my_board/tests/conftest.py my-board/my_board/tests/test_board.py
git commit -m "chore: scaffold flask board project and test harness"
```

### Task 2: Add SQLite schema and DB helpers via TDD

**Files:**
- Modify: `my-board/my_board/app.py`
- Modify: `my-board/my_board/tests/conftest.py`
- Modify: `my-board/my_board/tests/test_board.py`

- [ ] **Step 1: Write failing schema test**

```python
# add in my-board/my_board/tests/test_board.py
import sqlite3


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
```

- [ ] **Step 2: Run targeted test to verify it fails**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest tests/test_board.py::test_init_db_creates_posts_table -v`
Expected: FAIL with import error for `init_db`.

- [ ] **Step 3: Implement DB connection + init_db**

```python
# replace my-board/my_board/app.py with
from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(g.app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=str(Path(app.instance_path) / "board.db"),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)

    @app.before_request
    def attach_app_to_g():
        g.app = app

    @app.get("/")
    def index():
        return "ok"

    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Initialized database.")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

- [ ] **Step 4: Run full tests to verify pass**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest -v`
Expected: PASS for schema + health tests.

- [ ] **Step 5: Commit DB foundation**

```bash
git add my-board/my_board/app.py my-board/my_board/tests/test_board.py
git commit -m "feat: add sqlite schema initialization for posts table"
```

### Task 3: Build list and detail read routes with templates

**Files:**
- Modify: `my-board/my_board/app.py`
- Create: `my-board/my_board/templates/base.html`
- Create: `my-board/my_board/templates/post_list.html`
- Create: `my-board/my_board/templates/post_detail.html`
- Create: `my-board/my_board/static/style.css`
- Modify: `my-board/my_board/tests/test_board.py`

- [ ] **Step 1: Write failing tests for list/detail rendering**

```python
# add in my-board/my_board/tests/test_board.py
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
```

- [ ] **Step 2: Run target tests to verify they fail**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest tests/test_board.py::test_list_page_shows_posts tests/test_board.py::test_detail_page_shows_post_content -v`
Expected: FAIL because routes/templates are not implemented.

- [ ] **Step 3: Implement read routes and templates**

```python
# update routes in my-board/my_board/app.py inside create_app
from flask import abort, render_template

@app.get("/")
def post_list():
    init_db()
    rows = get_db().execute(
        "SELECT id, title, content, created_at FROM posts ORDER BY id DESC"
    ).fetchall()
    return render_template("post_list.html", posts=rows)

@app.get("/posts/<int:post_id>")
def post_detail(post_id: int):
    init_db()
    post = get_db().execute(
        "SELECT id, title, content, created_at FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()
    if post is None:
        abort(404)
    return render_template("post_detail.html", post=post)
```

```html
<!-- my-board/my_board/templates/base.html -->
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{% block title %}Linen & Logic Board{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Newsreader:opsz,wght@6..72,400;500&family=Work+Sans:wght@500;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
  </head>
  <body>
    <header class="topbar">
      <div class="topbar-inner">
        <a class="brand" href="{{ url_for('post_list') }}">Linen & Logic</a>
        <nav class="nav">
          <a href="{{ url_for('post_list') }}">Archive</a>
          <a href="{{ url_for('post_new') }}">Write</a>
        </nav>
      </div>
    </header>
    <main class="container">
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

```html
<!-- my-board/my_board/templates/post_list.html -->
{% extends 'base.html' %}
{% block title %}게시글 목록{% endblock %}
{% block content %}
<section class="page-head">
  <h1>Reflections on Architecture and Intentional Design.</h1>
  <a class="button" href="{{ url_for('post_new') }}">Start Writing</a>
</section>
<section class="post-list">
  {% for post in posts %}
    <article class="post-item">
      <p class="meta">{{ post.created_at }}</p>
      <h2><a href="{{ url_for('post_detail', post_id=post.id) }}">{{ post.title }}</a></h2>
      <p>{{ post.content[:180] }}{% if post.content|length > 180 %}...{% endif %}</p>
    </article>
  {% else %}
    <p>아직 게시글이 없습니다. 첫 글을 작성해보세요.</p>
  {% endfor %}
</section>
{% endblock %}
```

```html
<!-- my-board/my_board/templates/post_detail.html -->
{% extends 'base.html' %}
{% block title %}{{ post.title }}{% endblock %}
{% block content %}
<article class="post-detail">
  <p class="meta">{{ post.created_at }}</p>
  <h1>{{ post.title }}</h1>
  <div class="body">{{ post.content }}</div>
  <p><a class="text-link" href="{{ url_for('post_list') }}">Back to List</a></p>
</article>
{% endblock %}
```

```css
/* my-board/my_board/static/style.css */
:root {
  --bg: #fafaef;
  --surface: #ebebe0;
  --text: #2d2d2d;
  --muted: #6a6a5a;
  --line: #d1d1c2;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: 'Newsreader', serif;
}
.topbar {
  position: sticky;
  top: 0;
  border-bottom: 1px solid var(--line);
  background: #f5f5dc;
}
.topbar-inner {
  max-width: 980px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.brand {
  color: var(--text);
  text-decoration: none;
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
  letter-spacing: .03em;
}
.nav a {
  margin-left: 16px;
  text-decoration: none;
  color: var(--muted);
  font-family: 'Work Sans', sans-serif;
  font-size: 13px;
  text-transform: uppercase;
}
.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px 80px;
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 16px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 24px;
}
.page-head h1 { font-family: 'Manrope', sans-serif; margin: 0; }
.button {
  text-decoration: none;
  background: var(--text);
  color: #f5f5dc;
  padding: 10px 16px;
  font-family: 'Work Sans', sans-serif;
  font-size: 12px;
  text-transform: uppercase;
}
.post-list { margin-top: 28px; display: grid; gap: 28px; }
.post-item { padding-bottom: 22px; border-bottom: 1px solid var(--line); }
.meta { color: var(--muted); font-family: 'Work Sans', sans-serif; font-size: 13px; }
.post-item h2 { margin: 6px 0 10px; font-family: 'Manrope', sans-serif; }
.post-item a { color: inherit; text-decoration: none; }
.post-detail h1 { font-family: 'Manrope', sans-serif; margin: 6px 0 20px; }
.post-detail .body { white-space: pre-wrap; line-height: 1.75; }
.text-link { color: var(--text); font-family: 'Work Sans', sans-serif; }
```

- [ ] **Step 4: Run tests to verify pass**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest -v`
Expected: PASS for list/detail tests.

- [ ] **Step 5: Commit read feature**

```bash
git add my-board/my_board/app.py my-board/my_board/templates/base.html my-board/my_board/templates/post_list.html my-board/my_board/templates/post_detail.html my-board/my_board/static/style.css my-board/my_board/tests/test_board.py
git commit -m "feat: implement post list and detail views"
```

### Task 4: Build create route and write form with validation

**Files:**
- Modify: `my-board/my_board/app.py`
- Create: `my-board/my_board/templates/post_form.html`
- Modify: `my-board/my_board/templates/base.html`
- Modify: `my-board/my_board/static/style.css`
- Modify: `my-board/my_board/tests/test_board.py`

- [ ] **Step 1: Write failing tests for create flow**

```python
# add in my-board/my_board/tests/test_board.py

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

    assert response.status_code == 200
    assert b" " not in response.data
    assert b"" not in response.data
```

- [ ] **Step 2: Run target tests to verify they fail**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest tests/test_board.py::test_new_post_page_renders tests/test_board.py::test_create_post_redirects_to_detail tests/test_board.py::test_create_post_rejects_blank_fields -v`
Expected: FAIL because write/create routes are not implemented.

- [ ] **Step 3: Implement write form and create route**

```python
# add imports in my-board/my_board/app.py
from datetime import datetime
from flask import abort, flash, redirect, render_template, request, url_for

# add routes inside create_app
@app.get("/posts/new")
def post_new():
    return render_template("post_form.html", form={"title": "", "content": ""})

@app.post("/posts")
def post_create():
    init_db()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        flash("제목과 본문을 입력해주세요.")
        return render_template("post_form.html", form={"title": title, "content": content}), 400

    db = get_db()
    db.execute(
        "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
        (title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()

    post_id = db.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1").fetchone()["id"]
    return redirect(url_for("post_detail", post_id=post_id))
```

```html
<!-- my-board/my_board/templates/base.html body main start block update -->
<main class="container">
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul class="flash-list">
        {% for message in messages %}
          <li class="flash-item">{{ message }}</li>
        {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
```

```html
<!-- my-board/my_board/templates/post_form.html -->
{% extends 'base.html' %}
{% block title %}Write Post{% endblock %}
{% block content %}
<section class="write-layout">
  <header class="write-head">
    <h1>Structured Editor</h1>
    <p>새 게시글을 작성하세요.</p>
  </header>
  <form class="write-form" method="post" action="{{ url_for('post_create') }}">
    <label for="title">Title</label>
    <input id="title" name="title" type="text" value="{{ form.title }}" placeholder="Entry Title" required />

    <label for="content">Content</label>
    <textarea id="content" name="content" rows="14" placeholder="Start your narrative..." required>{{ form.content }}</textarea>

    <div class="actions">
      <button type="submit">Publish</button>
    </div>
  </form>
</section>
{% endblock %}
```

```css
/* add in my-board/my_board/static/style.css */
.flash-list {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
}
.flash-item {
  border: 1px solid #ba1a1a;
  background: #ffdad6;
  color: #93000a;
  padding: 10px 12px;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
}
.write-layout { max-width: 800px; }
.write-head h1 { margin: 0; font-family: 'Manrope', sans-serif; }
.write-head p { margin-top: 8px; color: var(--muted); }
.write-form { margin-top: 20px; display: grid; gap: 10px; }
.write-form label {
  font-family: 'Work Sans', sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  color: var(--muted);
}
.write-form input,
.write-form textarea {
  width: 100%;
  border: 1px solid var(--line);
  background: #fff;
  padding: 12px;
  font: inherit;
}
.actions { margin-top: 8px; }
.actions button {
  border: none;
  background: var(--text);
  color: #f5f5dc;
  padding: 11px 16px;
  font-family: 'Work Sans', sans-serif;
  text-transform: uppercase;
  font-size: 12px;
}
```

- [ ] **Step 4: Update blank-field test assertion for flash message**

```python
# update in my-board/my_board/tests/test_board.py

def test_create_post_rejects_blank_fields(client):
    response = client.post(
        "/posts",
        data={"title": "", "content": ""},
        follow_redirects=True,
    )

    assert response.status_code == 400
    assert "제목과 본문을 입력해주세요.".encode("utf-8") in response.data
```

- [ ] **Step 5: Run full tests to verify pass**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/pytest -v`
Expected: PASS for create/list/detail suite.

- [ ] **Step 6: Commit create feature**

```bash
git add my-board/my_board/app.py my-board/my_board/templates/base.html my-board/my_board/templates/post_form.html my-board/my_board/static/style.css my-board/my_board/tests/test_board.py
git commit -m "feat: add post create flow with minimal validation"
```

### Task 5: Manual verification on Ubuntu 24.04

**Files:**
- Modify: none

- [ ] **Step 1: Initialize local DB**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/flask --app app init-db`
Expected: `Initialized database.` 출력.

- [ ] **Step 2: Start development server**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/my_board && .venv/bin/flask --app app run --debug`
Expected: Flask dev server starts at `http://127.0.0.1:5000`.

- [ ] **Step 3: Verify golden path in browser**

Check:
1. `/` 목록 페이지 렌더링 및 공통 헤더/톤 확인.
2. `/posts/new`에서 제목/본문 입력 후 Publish.
3. 생성 후 상세 페이지로 리다이렉트 확인.
4. 다시 `/`로 이동해 새 글이 최상단에 표시되는지 확인.

- [ ] **Step 4: Verify edge case**

Check:
1. `/posts/new`에서 빈 제목/본문 제출.
2. 검증 메시지 표시 및 400 응답 확인.
3. 존재하지 않는 `/posts/999999` 접근 시 404 확인.

- [ ] **Step 5: Final commit for verification tweaks (if any)**

```bash
git add my-board/my_board
git commit -m "style: align board pages with linen and logic theme"
```

## Self-Review Notes

- Spec coverage:
  - C/R/R routes + SQLite schema + venv/test flow + Linen & Logic 공통 레이아웃 반영 + 3개 화면 반영 계획 포함.
- Placeholder scan:
  - `TBD/TODO` 같은 placeholder 없음.
- Type/signature consistency:
  - `create_app`, `init_db`, `get_db`, route names(`post_list`, `post_new`, `post_create`, `post_detail`) 일관성 유지.
