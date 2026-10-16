import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.database import engine, Base  # noqa: E402
from app import models  # noqa: E402,F401


def _reset_db():
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass
    Base.metadata.create_all(bind=engine)


_reset_db()
client = TestClient(app)
