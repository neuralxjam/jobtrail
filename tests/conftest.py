import uuid
from collections.abc import Generator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth import current_user
from app.database import get_session
from app.main import app
from app.models import Application  # noqa: F401 — registers table metadata

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@dataclass
class FakeUser:
    id: uuid.UUID
    email: str


USER_A = FakeUser(id=uuid.uuid4(), email="user_a@test.com")
USER_B = FakeUser(id=uuid.uuid4(), email="user_b@test.com")


def _override_session() -> Generator[Session, None, None]:
    with Session(TEST_ENGINE) as session:
        yield session


class _UserClient(TestClient):
    """Re-applies the correct user override before every request.

    Needed because two fixtures sharing app.dependency_overrides would
    overwrite each other at setup time.
    """

    def __init__(self, user: FakeUser | None) -> None:
        super().__init__(app, follow_redirects=False)
        self._user = user

    def request(self, method, url, **kwargs):
        app.dependency_overrides[get_session] = _override_session
        if self._user is not None:
            # default-arg capture avoids closure-over-loop-variable issues
            app.dependency_overrides[current_user] = lambda u=self._user: u
        else:
            app.dependency_overrides.pop(current_user, None)
        return super().request(method, url, **kwargs)


@pytest.fixture(autouse=True)
def reset_db():
    SQLModel.metadata.create_all(TEST_ENGINE)
    yield
    SQLModel.metadata.drop_all(TEST_ENGINE)
    app.dependency_overrides.clear()


@pytest.fixture
def client_a():
    return _UserClient(USER_A)


@pytest.fixture
def client_b():
    return _UserClient(USER_B)


@pytest.fixture
def anon_client():
    return _UserClient(None)
