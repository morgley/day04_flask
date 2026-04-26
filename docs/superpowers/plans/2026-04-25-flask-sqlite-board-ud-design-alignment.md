# Flask SQLite Board U/D + Design Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing Flask+SQLite board with update/delete flows while aligning list/write visuals closer to the provided design references using minimal file changes.

**Architecture:** Keep the current SSR Flask structure and add three U/D routes (`GET edit`, `POST edit`, `POST delete`) in `app.py`. Reuse `post_form.html` for both create and edit by passing explicit mode/action context. Adjust only existing templates/styles (`post_detail`, `post_list`, `post_form`, `style.css`) to improve design fidelity to `post_list_minimalist_text` and `write_post_sidebar_editor`.

**Tech Stack:** Python 3.12, Flask, sqlite3, Jinja2, pytest

---

## File Structure

- Modify: `my_board/app.py` — add edit/delete routes, reuse form context, keep existing create/list/detail intact.
- Modify: `my_board/templates/post_form.html` — support create/edit mode in one shared form.
- Modify: `my_board/templates/post_detail.html` — add [수정]/[삭제] actions with delete confirm.
- Modify: `my_board/templates/post_list.html` — tune layout/typography/button hierarchy toward target design.
- Modify: `my_board/static/style.css` — minimal style additions for action row + design alignment tweaks.
- Modify: `my_board/tests/test_board.py` — add/extend U/D and design-relevant behavior tests.

### Task 1: Add update route flow via shared form

**Files:**
- Modify: `my_board/tests/test_board.py`
- Modify: `my_board/app.py`
- Modify: `my_board/templates/post_form.html`

- [ ] **Step 1: Write failing tests for edit page and successful update**

```python
# add to my_board/tests/test_board.py

def test_edit_page_renders_existing_post(client, app):
    post_id = _seed_post(app, title="Before Edit", content="Before Body")

    response = client.get(f"/posts/{post_id}/edit")

    assert response.status_code == 200
    assert b"Before Edit" in response.data
    assert b"Before Body" in response.data


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
```

- [ ] **Step 2: Run targeted tests to verify RED**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest tests/test_board.py::test_edit_page_renders_existing_post tests/test_board.py::test_edit_post_updates_and_redirects -v`
Expected: FAIL with missing `/posts/<id>/edit` route.

- [ ] **Step 3: Implement edit GET/POST routes with minimal validation**

```python
# add imports in my_board/app.py (if missing)
from flask import request

# add inside create_app in my_board/app.py
@app.get("/posts/<int:post_id>/edit")
def post_edit(post_id: int):
    init_db()
    post = get_db().execute(
        "SELECT id, title, content, created_at FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()
    if post is None:
        abort(404)
    return render_template(
        "post_form.html",
        mode="edit",
        post=post,
        form={"title": post["title"], "content": post["content"]},
        form_action=url_for("post_update", post_id=post_id),
    )

@app.post("/posts/<int:post_id>/edit")
def post_update(post_id: int):
    init_db()
    post = get_db().execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        abort(404)

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        flash("제목과 본문을 입력해주세요.")
        return (
            render_template(
                "post_form.html",
                mode="edit",
                post={"id": post_id},
                form={"title": title, "content": content},
                form_action=url_for("post_update", post_id=post_id),
            ),
            400,
        )

    db = get_db()
    db.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (title, content, post_id),
    )
    db.commit()
    return redirect(url_for("post_detail", post_id=post_id))
```

```html
<!-- update my_board/templates/post_form.html -->
{% extends 'base.html' %}
{% block title %}{% if mode == 'edit' %}Edit Post{% else %}Write Post{% endif %}{% endblock %}
{% block content %}
<section class="write-layout">
  <header class="write-head">
    <h1>{% if mode == 'edit' %}Edit{% else %}Write{% endif %}</h1>
    <p>{% if mode == 'edit' %}게시글을 수정하세요.{% else %}새 게시글을 작성하세요.{% endif %}</p>
  </header>
  <form class="write-form" method="post" action="{{ form_action }}">
    <label for="title">Title</label>
    <input id="title" name="title" type="text" value="{{ form.title }}" placeholder="Entry Title" required />

    <label for="content">Content</label>
    <textarea id="content" name="content" rows="14" placeholder="Start your narrative..." required>{{ form.content }}</textarea>

    <div class="actions">
      <button type="submit">{% if mode == 'edit' %}Update{% else %}Publish{% endif %}</button>
    </div>
  </form>
</section>
{% endblock %}
```

- [ ] **Step 4: Keep create route using shared form context**

```python
# update existing create route rendering in my_board/app.py
@app.get("/posts/new")
def post_new():
    return render_template(
        "post_form.html",
        mode="create",
        post=None,
        form={"title": "", "content": ""},
        form_action=url_for("post_create"),
    )

# update invalid create branch similarly
return (
    render_template(
        "post_form.html",
        mode="create",
        post=None,
        form={"title": title, "content": content},
        form_action=url_for("post_create"),
    ),
    400,
)
```

- [ ] **Step 5: Run full tests to verify GREEN**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest -v`
Expected: PASS including new edit tests.

- [ ] **Step 6: Commit Task 1**

```bash
git add my_board/app.py my_board/templates/post_form.html my_board/tests/test_board.py
git commit -m "feat: add post edit flow with shared form template"
```

### Task 2: Add delete action with confirmation and route

**Files:**
- Modify: `my_board/tests/test_board.py`
- Modify: `my_board/app.py`
- Modify: `my_board/templates/post_detail.html`
- Modify: `my_board/static/style.css`

- [ ] **Step 1: Write failing tests for delete behavior**

```python
# add to my_board/tests/test_board.py

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
```

- [ ] **Step 2: Run targeted tests to verify RED**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest tests/test_board.py::test_delete_post_removes_record_and_redirects tests/test_board.py::test_delete_missing_post_returns_404 -v`
Expected: FAIL due to missing delete route.

- [ ] **Step 3: Implement delete POST route**

```python
# add inside create_app in my_board/app.py
@app.post("/posts/<int:post_id>/delete")
def post_delete(post_id: int):
    init_db()
    db = get_db()
    post = db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        abort(404)

    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    return redirect(url_for("post_list"))
```

- [ ] **Step 4: Add edit/delete buttons and confirm dialog on detail page**

```html
<!-- update my_board/templates/post_detail.html -->
{% extends 'base.html' %}
{% block title %}{{ post.title }}{% endblock %}
{% block content %}
<article class="post-detail">
  <p class="meta">{{ post.created_at }}</p>
  <h1>{{ post.title }}</h1>
  <div class="body">{{ post.content }}</div>
  <div class="detail-actions">
    <a class="button-secondary" href="{{ url_for('post_edit', post_id=post.id) }}">수정</a>
    <form method="post" action="{{ url_for('post_delete', post_id=post.id) }}" onsubmit="return confirm('정말 삭제할까요?')">
      <button class="button-danger" type="submit">삭제</button>
    </form>
  </div>
  <p><a class="text-link" href="{{ url_for('post_list') }}">Back to List</a></p>
</article>
{% endblock %}
```

```css
/* add to my_board/static/style.css */
.detail-actions {
  margin: 18px 0 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.detail-actions form {
  margin: 0;
}

.button-secondary,
.button-danger {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--text);
  padding: 8px 12px;
  text-decoration: none;
  font-family: "Work Sans", sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  cursor: pointer;
}

.button-danger {
  border-color: #ba1a1a;
  color: #ba1a1a;
}
```

- [ ] **Step 5: Run full tests to verify GREEN**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest -v`
Expected: PASS including delete tests.

- [ ] **Step 6: Commit Task 2**

```bash
git add my_board/app.py my_board/templates/post_detail.html my_board/static/style.css my_board/tests/test_board.py
git commit -m "feat: add post delete route and detail page actions"
```

### Task 3: Align list/write design closer to reference templates

**Files:**
- Modify: `my_board/templates/post_list.html`
- Modify: `my_board/templates/post_form.html`
- Modify: `my_board/static/style.css`
- Test: `my_board/tests/test_board.py`

- [ ] **Step 1: Write failing HTML-structure assertions for key design anchors**

```python
# add to my_board/tests/test_board.py

def test_list_page_has_start_writing_cta(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Start Writing" in response.data


def test_write_form_has_editor_heading(client):
    response = client.get("/posts/new")
    assert response.status_code == 200
    assert b"Structured Editor" in response.data
```

- [ ] **Step 2: Run targeted tests to verify RED**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest tests/test_board.py::test_list_page_has_start_writing_cta tests/test_board.py::test_write_form_has_editor_heading -v`
Expected: FAIL because current templates do not include these anchor texts.

- [ ] **Step 3: Update list template structure toward post_list_minimalist_text**

```html
<!-- replace body block in my_board/templates/post_list.html -->
{% extends 'base.html' %}
{% block title %}게시글 목록{% endblock %}
{% block content %}
<section class="page-head">
  <div>
    <span class="kicker">Archive &amp; Essays</span>
    <h1>Reflections on Architecture and Intentional Design.</h1>
  </div>
  <a class="button-primary" href="{{ url_for('post_new') }}">Start Writing</a>
</section>
<section class="post-list">
  {% for post in posts %}
    <article class="post-item">
      <p class="meta">{{ post.created_at }}</p>
      <h2><a href="{{ url_for('post_detail', post_id=post.id) }}">{{ post.title }}</a></h2>
      <p>{{ post.content[:180] }}{% if post.content|length > 180 %}...{% endif %}</p>
      <a class="read-link" href="{{ url_for('post_detail', post_id=post.id) }}">Read Essay</a>
    </article>
  {% else %}
    <p>아직 게시글이 없습니다.</p>
  {% endfor %}
</section>
{% endblock %}
```

- [ ] **Step 4: Update form template header toward write_post_sidebar_editor tone**

```html
<!-- update header block in my_board/templates/post_form.html -->
<header class="write-head">
  <h1>Structured Editor</h1>
  <p>{% if mode == 'edit' %}게시글을 수정하세요.{% else %}새 게시글을 작성하세요.{% endif %}</p>
</header>
```

- [ ] **Step 5: Add minimal style tweaks for design hierarchy**

```css
/* add to my_board/static/style.css */
.kicker {
  display: inline-block;
  margin-bottom: 10px;
  color: var(--muted);
  font-family: "Work Sans", sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.button-primary {
  text-decoration: none;
  background: var(--text);
  color: #f5f5dc;
  padding: 10px 16px;
  font-family: "Work Sans", sans-serif;
  font-size: 12px;
  text-transform: uppercase;
}

.read-link {
  display: inline-block;
  margin-top: 8px;
  color: var(--text);
  font-family: "Work Sans", sans-serif;
  font-size: 12px;
  text-transform: uppercase;
  text-decoration: none;
  border-bottom: 1px solid var(--text);
}
```

- [ ] **Step 6: Run full tests to verify GREEN**

Run: `cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/python -m pytest -v`
Expected: PASS including design anchor tests.

- [ ] **Step 7: Manual browser verification of layout fidelity**

Run server:
`cd /home/morgley/Workspaces/claude_code_workspace/day04/my-board/.worktrees/flask-board-crr/my_board && .venv/bin/flask --app app run --debug`

Check in browser:
1. `http://127.0.0.1:5000/` shows Start Writing CTA and stronger list typography hierarchy.
2. `http://127.0.0.1:5000/posts/new` shows Structured Editor heading and adjusted editor tone.
3. `http://127.0.0.1:5000/posts/<id>` shows 수정/삭제 actions with confirm on delete.

- [ ] **Step 8: Commit Task 3**

```bash
git add my_board/templates/post_list.html my_board/templates/post_form.html my_board/static/style.css my_board/tests/test_board.py
git commit -m "style: align list and editor screens with reference design tone"
```

## Self-Review Notes

- Spec coverage:
  - U/D routes, detail actions, shared form reuse, delete confirm dialog, and design alignment for list/write are all mapped to tasks.
- Placeholder scan:
  - No TBD/TODO/placeholders.
- Type/signature consistency:
  - Route names (`post_edit`, `post_update`, `post_delete`) and template context keys (`mode`, `form_action`, `form`, `post`) are used consistently across tasks.
