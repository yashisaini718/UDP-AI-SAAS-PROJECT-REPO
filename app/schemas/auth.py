## all pydantic models
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token : str
    token_type : str

class RegisterUser(BaseModel):
    username: str= Field(min_length=5,max_length=20)
    email: EmailStr
    password: str= Field(min_length=5,max_length=15)

class RegisteredUser(BaseModel):
    username: str
    email: EmailStr

class LoginUser(BaseModel):
    username: str
    password: str