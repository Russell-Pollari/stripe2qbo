from typing import Annotated
import os

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv

from stripe2qbo.api.dependencies import get_db
from stripe2qbo.api.routers import (
    qbo,
    stripe_router,
    transaction_router,
    settings,
    sync,
)
from stripe2qbo.db.models import User as UserORM
from stripe2qbo.db.schemas import User
from stripe2qbo.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    get_password_hash,
)

load_dotenv()

app = FastAPI()


if not os.path.exists("static"):
    os.mkdir("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(qbo.router, prefix="/api")
app.include_router(stripe_router.router, prefix="/api")
app.include_router(transaction_router.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.post("/api/token")
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> str:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token, expires = create_access_token(user.email)
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        samesite="strict",
        # expires=expires,
        secure=os.getenv("SSL", "false").lower() == "true",
    )
    return "ok"


@app.post("/api/logout")
def logout(response: Response) -> str:
    response.delete_cookie(
        key="token",
        secure=os.getenv("SSL", "false").lower() == "true",
    )
    return "ok"


@app.post("/api/signup")
def signup(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> str:
    if db.query(UserORM).filter(UserORM.email == form_data.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = UserORM(
        email=form_data.username,
        hashed_password=get_password_hash(form_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token, expires = create_access_token(user.email)
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        samesite="strict",
        # expires=expires,
        secure=os.getenv("SSL", "false").lower() == "true",
    )
    return "ok"


@app.get("/api/userId")
def user_id(user: Annotated[UserORM, Depends(get_current_user_from_token)]) -> User:
    return User.model_validate(user, from_attributes=True)


@app.get("/{path:path}")
def catch_all(path: str) -> HTMLResponse:
    return HTMLResponse(
        content="""
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Stripe2QBO</title>
                    <link rel="stylesheet" href="/static/index.css">
                </head>
                <body>
                    <div id="root"></div>
                    <script src="/static/index.js"></script>
                </body>
            </html>
        """,
        status_code=200,
    )
