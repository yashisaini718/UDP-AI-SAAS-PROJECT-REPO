from app.core.security import generate_password, create_access_token, authenticate_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from datetime import timedelta
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import Token, RegisteredUser
from app.core.config import config


async def registeruser(db: AsyncSession, password: str, username: str, email: str)-> RegisteredUser:
    hashed_password = generate_password(password)

    result = await db.execute(select(User).where(User.username == username))

    username_exist = result.scalar_one_or_none()

    if username_exist:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= "Username not available",
        )

    result = await db.execute(select(User).where(User.email == email))

    email_exist = result.scalar_one_or_none()

    if email_exist:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail= "Email already used",
        )

    new_user = User(
        username= username,
        email= email,
        hashed_password= hashed_password,
    )

    db.add(new_user)

    await db.flush()

    await db.commit()

    await db.refresh(new_user)

    return RegisteredUser(
        username= new_user.username,
        email= new_user.email
    )


async def create_login( form_data: OAuth2PasswordRequestForm, db: AsyncSession) -> Token:
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid username or password",
            headers= {"WWW-Authenticate": "Bearer"},
        )
    print (config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(
        minutes= config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data= {"sub": user.username},
        expires_delta= access_token_expires,
    )

    return Token(
        access_token= access_token,
        token_type= "bearer",
    )