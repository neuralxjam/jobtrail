import os

from dotenv import load_dotenv
from fastapi import Request
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class UnauthenticatedException(Exception):
    pass


async def current_user(request: Request):
    token = request.cookies.get("sb-token")
    if not token:
        raise UnauthenticatedException()
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        raise UnauthenticatedException()
