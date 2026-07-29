from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import config
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.models.users import User
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

password_hash=PasswordHash.recommended()

def generate_password(password:str):
    return password_hash.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    return password_hash.verify(plain_password,hashed_password)

def create_access_token(data:dict, expires_delta:timedelta | None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=60)
    to_encode.update({"exp" : expire})
    encoded_jwt=jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def verify_token(token:str):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    try:
        payload=jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username=payload.get("sub")
        if username is None :
            raise credentials_exception
        return username
    except InvalidTokenError :
        raise credentials_exception

async def authenticate_user(username: str,password: str,db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db),):
    username = verify_token(token)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    return user