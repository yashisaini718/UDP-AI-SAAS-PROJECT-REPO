## all pydantic models
from pydantic import BaseModel

class Token(BaseModel):
    access_token : str
    token_type : str

class RegisteredUser(BaseModel):
    username: str
    email: str