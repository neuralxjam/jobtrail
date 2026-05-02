import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Request
from supabase import Client, create_client

load_dotenv()


@lru_cache(maxsize=1)
def _client() -> Client:
    """Lazy singleton — not created until first auth call, so tests without credentials work."""
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


class _SupabaseProxy:
    def __getattr__(self, name):
        return getattr(_client(), name)


supabase = _SupabaseProxy()


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
