from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.models import Application  # noqa: F401 — registers table with SQLModel metadata
from app.routes.applications import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="JobTrail", lifespan=lifespan)
app.include_router(router)
