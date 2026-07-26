from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from app.auth.schemas import Token, RegisteredUser
from app.core.config import config
from app.core.security import generate_password, create_access_token, authenticate_user
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=RegisteredUser)
async def register_user(
    username: str,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    hashed_password = generate_password(password)

    result = await db.execute(
        select(User).where(User.username == username)
    )
    username_exist = result.scalar_one_or_none()

    if username_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username not available",
        )

    result = await db.execute(
        select(User).where(User.email == email)
    )
    email_exist = result.scalar_one_or_none()

    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already used",
        )

    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    db.add(new_user)

    await db.flush()

    await db.commit()

    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        formdata.username,
        formdata.password,
        db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print (config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )