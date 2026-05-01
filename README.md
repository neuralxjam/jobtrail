# JobTrail

> Track every job application in one place — statuses, notes, dashboard, and weekly activity chart.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white)

**Live demo**: *(link coming)*

---

## What it does

Managing job applications in a spreadsheet loses context fast. JobTrail is a personal web app where you log every application — company, role, date, status, notes — and see it on a dashboard with filtering and weekly activity tracking.

## Tech stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI + SQLModel |
| Database | PostgreSQL via Supabase |
| Frontend | Jinja2 + HTMX + Tailwind CSS |
| Auth | Supabase magic-link email auth |
| Deploy | Render (free tier) |
| CI | GitHub Actions |

## Local setup

```bash
git clone https://github.com/neuralxjam/jobtrail
cd jobtrail

# Install dependencies
pip install uv
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your Supabase credentials in .env

# Run
uvicorn app.main:app --reload
# Open http://localhost:8000
```

## Project structure

```
jobtrail/
├── app/
│   ├── main.py          ← FastAPI app + routes
│   ├── models.py        ← SQLModel database models
│   ├── routes/          ← Route handlers by feature
│   └── templates/       ← Jinja2 HTML templates
├── tests/               ← pytest test suite
├── render.yaml          ← Render deploy config
└── requirements.txt
```
