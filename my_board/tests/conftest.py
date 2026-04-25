from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
