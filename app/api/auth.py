from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.config import Config

from app.config import settings
from app.db.session import get_conn
from app.dependencies import get_current_user
from app.services.auth import create_access_token
from app.users.dao import create_user, get_user_by_google_id, update_user

router = APIRouter(prefix="/auth")

_config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.google_client_id,
    "GOOGLE_CLIENT_SECRET": settings.google_client_secret,
})

oauth = OAuth(_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, conn: AsyncConnection = Depends(get_conn)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo") or await oauth.google.userinfo(token=token)

    google_id = userinfo["sub"]
    email = userinfo.get("email", "")
    name = userinfo.get("name", email)
    picture = userinfo.get("picture")

    existing = await get_user_by_google_id(conn, google_id)
    if existing is None:
        user = await create_user(conn, google_id, email, name, picture)
    else:
        await update_user(conn, google_id, name, picture)
        user = {**existing, "name": name, "picture": picture}

    await conn.commit()

    jwt_token = create_access_token({"sub": user["id"], "name": user["name"], "email": user["email"]})

    response = RedirectResponse(url="/?after_login=1")
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_expire_hours * 3600,
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/me")
async def me(current_user: dict | None = Depends(get_current_user)):
    if not current_user:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    return {"id": current_user["sub"], "name": current_user["name"], "email": current_user["email"]}
