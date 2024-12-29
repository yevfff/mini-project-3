from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# USER SCHEMAS
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
        orm_mode = True


# ITEM SCHEMAS
class ItemCreate(BaseModel):
    title: str
    description: str
    category: str
    price: float
    location: Optional[str]


class ItemView(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    location: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class ItemFilter(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    search: Optional[str] = None


class Pagination(BaseModel):
    page: int = 1
    size: int = 10


# TOKEN SCHEMAS
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int



# CHAT
class ChatMessage(BaseModel):
    sender_id: int
    recipient_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True


class ChatSummary(BaseModel):
    partner_id: int
    last_message: str
    timestamp: datetime
