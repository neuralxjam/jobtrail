from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import Application, ApplicationStatus

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/", response_class=HTMLResponse)
async def list_applications(request: Request, session: Session = Depends(get_session)):
    applications = session.exec(
        select(Application).order_by(Application.date_applied.desc())
    ).all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"applications": applications}
    )


@router.get("/applications/new", response_class=HTMLResponse)
async def new_application_form(request: Request):
    return templates.TemplateResponse(
        request=request, name="partials/application_form.html", context={"app": None}
    )


@router.get("/applications/cancel", response_class=HTMLResponse)
async def cancel_form():
    return HTMLResponse("")


@router.get("/filter", response_class=HTMLResponse)
async def filter_applications(
    request: Request,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(Application).order_by(Application.date_applied.desc())
    if status and status != "all":
        query = query.where(Application.status == status)
    applications = session.exec(query).all()
    return templates.TemplateResponse(
        request=request,
        name="partials/application_rows.html",
        context={"applications": applications, "active_status": status},
    )


@router.post("/applications", response_class=HTMLResponse)
async def create_application(
    request: Request,
    company: str = Form(...),
    role: str = Form(...),
    status: ApplicationStatus = Form(ApplicationStatus.applied),
    date_applied: date = Form(...),
    job_url: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    application = Application(
        company=company,
        role=role,
        status=status,
        date_applied=date_applied,
        job_url=job_url or None,
        notes=notes or None,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return templates.TemplateResponse(
        request=request,
        name="partials/application_row.html",
        context={"app": application},
    )


@router.get("/applications/{app_id}/edit", response_class=HTMLResponse)
async def edit_application_form(
    request: Request, app_id: int, session: Session = Depends(get_session)
):
    application = session.get(Application, app_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/application_edit_row.html",
        context={"app": application},
    )


@router.get("/applications/{app_id}/row", response_class=HTMLResponse)
async def get_application_row(
    request: Request, app_id: int, session: Session = Depends(get_session)
):
    application = session.get(Application, app_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/application_row.html",
        context={"app": application},
    )


@router.put("/applications/{app_id}", response_class=HTMLResponse)
async def update_application(
    request: Request,
    app_id: int,
    company: str = Form(...),
    role: str = Form(...),
    status: ApplicationStatus = Form(...),
    date_applied: date = Form(...),
    job_url: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    application = session.get(Application, app_id)
    application.company = company
    application.role = role
    application.status = status
    application.date_applied = date_applied
    application.job_url = job_url or None
    application.notes = notes or None
    session.add(application)
    session.commit()
    session.refresh(application)
    return templates.TemplateResponse(
        request=request,
        name="partials/application_row.html",
        context={"app": application},
    )


@router.delete("/applications/{app_id}", response_class=HTMLResponse)
async def delete_application(app_id: int, session: Session = Depends(get_session)):
    application = session.get(Application, app_id)
    session.delete(application)
    session.commit()
    return HTMLResponse("")
