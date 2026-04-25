from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

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


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
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


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    init_db()
    click.echo("Initialized the database.")


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get("DATABASE", str(Path(app.instance_path) / "board.db")),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    @app.get("/")
    def post_list():
        init_db()
        posts = get_db().execute(
            "SELECT id, title, content, created_at FROM posts ORDER BY id DESC"
        ).fetchall()
        return render_template("post_list.html", posts=posts)

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

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
