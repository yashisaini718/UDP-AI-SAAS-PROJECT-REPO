from fastapi import Request, Response
from app.core.security import generate_password, create_access_token, create_refresh_token, authenticate_user, logout_current_user, verify_refresh_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from datetime import timedelta
from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy import select
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import Token, RegisteredUser, LoginUser
from app.core.config import config
import jwt


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


async def create_login( form_data: LoginUser, db: AsyncSession) -> Token:
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

    access_token_expires = timedelta(
        minutes= config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data= {"sub": user.username},
        expires_delta= access_token_expires,
    )

    refresh_token = create_refresh_token(
        data= {"sub": user.username}
    )

    response= JSONResponse(content={"message":"Login Successful"})

    response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
    return response


async def refresh_access_token(request: Request, response: Response):

    try:
        token=request.cookies.get("refresh_token")

        payload=await verify_refresh_token(token)

        data=payload["sub"]

        new_access_token= create_access_token(data= {"sub" : data})

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        
        return  {"message": "Access token refreshed"}

    except Exception as e :
        print (e)
        raise e
        #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials")


async def logout_user(request: Request, response: Response):

    token=request.cookies.get("refresh_token")

    payload=jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

    jti= payload["jti"]
    exp=payload["exp"]

    ttl= exp - int(datetime.now(timezone.utc).timestamp())

    await logout_current_user(jti, ttl)

    response.delete_cookie("access_token")

    response.delete_cookie("refresh_token")

    return {"message" : "User logged out successfully !"}