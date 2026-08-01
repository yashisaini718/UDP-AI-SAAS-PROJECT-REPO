from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import registeruser, create_login, logout_user, refresh_access_token
from app.schemas.auth import Token, RegisteredUser, LoginUser, RegisterUser
from app.db.session import get_db
from app.core.security import get_current_user


router = APIRouter(prefix= "/auth", tags= ["Auth"])

''' Routes for registering and login'''

@router.post("/register", response_model= RegisteredUser)
async def register_user(
   user: RegisterUser, 
    db: AsyncSession = Depends(get_db)
):
    
    return await registeruser(username=user.username, email=user.email, password=user.password, db=db)


@router.post("/login")
async def login(
    data: LoginUser,
    db: AsyncSession = Depends(get_db),
):
    
    return await create_login(form_data=data, db=db)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):

    return await refresh_access_token(request=request, response=response)


@router.post("/logout")
async def logout(request: Request, response: Response):

    return await logout_user(request=request, response=response)