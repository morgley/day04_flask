from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import libsql

import click
from flask import (
    Flask,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.cli import with_appcontext


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _row_to_dict(cursor, row):
    if row is None:
        return None
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def get_db():
    if "db" not in g:
        database_url = current_app.config["DATABASE"]
        auth_token = current_app.config.get("TURSO_AUTH_TOKEN")

        if database_url.startswith("libsql://"):
            g.db = libsql.connect(database=database_url, auth_token=auth_token)
        else:
            g.db = libsql.connect(database_url)

        if hasattr(g.db, "row_factory"):
            g.db.row_factory = _row_to_dict
    return g.db


def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    init_db()
    click.echo("Initialized the database.")


def create_app(test_config: dict | None = None) -> Flask:
    project_root = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        instance_relative_config=True,
        root_path=str(project_root),
        instance_path=str(project_root / "instance"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get(
            "TURSO_DATABASE_URL",
            os.environ.get("DATABASE", str(Path(app.instance_path) / "board.db")),
        ),
        TURSO_AUTH_TOKEN=os.environ.get("TURSO_AUTH_TOKEN"),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    @app.get("/")
    def post_list():
        init_db()

        q = request.args.get("q", "").strip()
        raw_sort = request.args.get("sort", "latest")
        sort_options = {
            "latest": "ORDER BY id DESC",
            "oldest": "ORDER BY id ASC",
            "title": "ORDER BY title COLLATE NOCASE ASC, id DESC",
        }
        sort = raw_sort if raw_sort in sort_options else "latest"

        raw_page = request.args.get("page", "1")
        try:
            page = int(raw_page)
        except (TypeError, ValueError):
            page = 1

        if page < 1:
            page = 1

        per_page = 10
        db = get_db()

        where_sql = ""
        params: list[str] = []
        if q:
            where_sql = "WHERE title LIKE ? OR content LIKE ?"
            like = f"%{q}%"
            params = [like, like]

        total_count_row = db.execute(
            f"SELECT COUNT(*) AS count FROM posts {where_sql}",
            tuple(params),
        ).fetchone()
        total_count = total_count_row[0]
        total_pages = max(1, (total_count + per_page - 1) // per_page)

        if page > total_pages:
            page = total_pages

        offset = (page - 1) * per_page
        posts_cursor = db.execute(
            f"SELECT id, title, content, created_at FROM posts {where_sql} {sort_options[sort]} LIMIT ? OFFSET ?",
            tuple([*params, per_page, offset]),
        )
        posts = [_row_to_dict(posts_cursor, row) for row in posts_cursor.fetchall()]

        return render_template(
            "post_list.html",
            posts=posts,
            page=page,
            total_pages=total_pages,
            has_prev=page > 1,
            has_next=page < total_pages,
            prev_page=page - 1,
            next_page=page + 1,
            q=q,
            sort=sort,
            is_search=bool(q),
            no_results=bool(q) and total_count == 0,
        )

    @app.get("/posts/new")
    def post_new():
        return render_template(
            "post_form.html",
            mode="create",
            post=None,
            form={"title": "", "content": ""},
            form_action=url_for("post_create"),
        )

    @app.post("/posts")
    def post_create():
        init_db()
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("제목과 본문을 입력해주세요.")
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

        db = get_db()
        cursor = db.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        db.commit()
        post_id = cursor.lastrowid
        return redirect(url_for("post_detail", post_id=post_id))

    @app.get("/posts/<int:post_id>/edit")
    def post_edit(post_id: int):
        init_db()
        post_cursor = get_db().execute(
            "SELECT id, title, content, created_at FROM posts WHERE id = ?",
            (post_id,),
        )
        post = _row_to_dict(post_cursor, post_cursor.fetchone())
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
        post_row = get_db().execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post_row is None:
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

    @app.post("/posts/<int:post_id>/delete")
    def post_delete(post_id: int):
        init_db()
        db = get_db()
        post_row = db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post_row is None:
            abort(404)

        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()
        return redirect(url_for("post_list"))

    @app.get("/posts/<int:post_id>")
    def post_detail(post_id: int):
        init_db()
        post_cursor = get_db().execute(
            "SELECT id, title, content, created_at FROM posts WHERE id = ?",
            (post_id,),
        )
        post = _row_to_dict(post_cursor, post_cursor.fetchone())
        if post is None:
            abort(404)
        return render_template("post_detail.html", post=post)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
