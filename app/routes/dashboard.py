import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, col, func, select

from app.auth import current_user
from app.database import get_session
from app.models import Application, ApplicationStatus

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

STATUS_STYLE = {
    "applied":      {"label": "Applied",      "bg": "bg-indigo-900/40", "border": "border-indigo-700", "text": "text-indigo-300"},
    "interviewing": {"label": "Interviewing",  "bg": "bg-amber-900/40",  "border": "border-amber-700",  "text": "text-amber-300"},
    "offered":      {"label": "Offered",       "bg": "bg-emerald-900/40","border": "border-emerald-700","text": "text-emerald-300"},
    "rejected":     {"label": "Rejected",      "bg": "bg-rose-900/40",   "border": "border-rose-700",   "text": "text-rose-300"},
    "ghosted":      {"label": "Ghosted",       "bg": "bg-slate-800/60",  "border": "border-slate-600",  "text": "text-slate-400"},
}


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    user=Depends(current_user),
):
    # --- status counts ---
    rows = session.exec(
        select(Application.status, func.count(col(Application.id)).label("n"))
        .where(Application.user_id == user.id)
        .group_by(Application.status)
    ).all()

    status_counts = {s.value: 0 for s in ApplicationStatus}
    for status, count in rows:
        status_counts[status] = count
    total = sum(status_counts.values())

    cards = [
        {**STATUS_STYLE[s], "count": status_counts[s]}
        for s in STATUS_STYLE
    ]

    # --- weekly chart (last 8 weeks, Mon–Sun buckets) ---
    today = date.today()
    weeks = []
    for i in range(7, -1, -1):
        monday = today - timedelta(weeks=i, days=today.weekday())
        weeks.append(monday)

    recent_dates = session.exec(
        select(Application.date_applied)
        .where(Application.user_id == user.id)
        .where(Application.date_applied >= weeks[0])
    ).all()

    weekly: dict[date, int] = defaultdict(int)
    for d in recent_dates:
        monday = d - timedelta(days=d.weekday())
        weekly[monday] += 1

    chart_labels = json.dumps([w.strftime("%b %d") for w in weeks])
    chart_data   = json.dumps([weekly.get(w, 0) for w in weeks])

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user_email": user.email,
            "cards": cards,
            "total": total,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
        },
    )
