from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# USER
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


class AdCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    category: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    location: Optional[str] = Field(None, max_length=100)

class AdView(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    location: Optional[str]
    created_at: str

    class Config:
        orm_mode = True

class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)


# TOKEN
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
