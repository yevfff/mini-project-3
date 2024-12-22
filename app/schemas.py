from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
