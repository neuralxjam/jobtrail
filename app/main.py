from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from app.auth import UnauthenticatedException
from app.database import create_db_and_tables
from app.models import Application  # noqa: F401 — registers table with SQLModel metadata
from app.routes.applications import router as applications_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="JobTrail", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(applications_router)


@app.exception_handler(UnauthenticatedException)
async def unauthenticated_handler(request: Request, exc: UnauthenticatedException):
    return RedirectResponse(url="/login")
