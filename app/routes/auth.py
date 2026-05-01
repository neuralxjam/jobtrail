from pathlib import Path

from fastapi import APIRouter, Body, Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import supabase

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

REDIRECT_URL = "http://localhost:8000/auth/callback"
COOKIE_OPTS = {"key": "sb-token", "httponly": True, "samesite": "lax", "secure": False, "max_age": 3600}


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"sent": False, "email": None, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
async def send_magic_link(request: Request, email: str = Form(...)):
    error = None
    try:
        supabase.auth.sign_in_with_otp(
            {"email": email, "options": {"email_redirect_to": REDIRECT_URL}}
        )
    except Exception as exc:
        error = str(exc)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"sent": error is None, "email": email, "error": error},
    )


@router.get("/auth/callback", response_class=HTMLResponse)
async def auth_callback(request: Request, code: str = None):
    # PKCE flow: code is a query param — exchange it server-side
    if code:
        try:
            session = supabase.auth.exchange_code_for_session({"auth_code": code})
            access_token = session.session.access_token
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(value=access_token, **COOKIE_OPTS)
            return response
        except Exception:
            return RedirectResponse(url="/login", status_code=303)

    # Implicit flow: token is in the URL hash — JS must extract and POST it
    return templates.TemplateResponse(request=request, name="auth_callback.html", context={})


@router.post("/auth/set-token")
async def set_token(token: str = Body(..., embed=True)):
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise ValueError("no user")
    except Exception:
        return JSONResponse({"error": "invalid token"}, status_code=401)

    response = JSONResponse({"ok": True})
    response.set_cookie(value=token, **COOKIE_OPTS)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("sb-token")
    return response
