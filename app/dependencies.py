from fastapi import Cookie

from app.services.auth import decode_access_token


async def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> dict | None:
    if not access_token:
        return None
    return decode_access_token(access_token)
