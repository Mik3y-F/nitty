import logging
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import app.auth.service as auth_service
from app.auth.models import Token, UserCreate, UserPublic, UserRegister
from app.config import settings
from app.database import DbSession

logger = logging.getLogger(__name__)

auth_router = APIRouter(tags=["auth"])


@auth_router.post("/login/access-token")
def login_access_token(
    session: DbSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth_service.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    logger.info(f"User: {user}")
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(
        access_token=auth_service.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@auth_router.post("/signup", response_model=UserPublic)
def register_user(session: DbSession, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = auth_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = auth_service.create_user(session=session, user_create=user_create)
    return user
