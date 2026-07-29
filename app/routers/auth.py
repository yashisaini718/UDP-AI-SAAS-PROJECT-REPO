from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth import registeruser, create_login
from app.schemas.auth import Token, RegisteredUser
from app.db.session import get_db


router = APIRouter(prefix= "/auth", tags= ["Auth"])

''' Routes for registering and login'''

@router.post("/register", response_model= RegisteredUser)
async def register_user(
    username: str, 
    email: str, 
    password: str, 
    db: AsyncSession = Depends(get_db)
):
    
    return await registeruser(username=username, email=email, password= password, db= db)


@router.post("/login", response_model= Token)
async def login(
    formdata: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    return await create_login(form_data= formdata, db= db)