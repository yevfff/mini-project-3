from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# USER SCHEMAS
class UserCreate(BaseModel):
    email: EmailStr = Field(..., title="Email address", description="The email address of the user.")
    password: str = Field(..., min_length=8, title="Password", description="The password for the user, at least 8 characters long.")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., title="Email address", description="The email address of the user.")
    password: str = Field(..., title="Password", description="The password for the user.")


class UserOut(BaseModel):
    id: int = Field(..., title="User ID", description="The unique identifier for the user.")
    email: EmailStr = Field(..., title="Email address", description="The email address of the user.")
    created_at: datetime = Field(..., title="Creation Date", description="The date and time when the user was created.")

    class Config:
        orm_mode = True


# ITEM SCHEMAS
class ItemCreate(BaseModel):
    title: str = Field(..., title="Item Title", description="The title of the item.")
    description: str = Field(..., title="Item Description", description="A detailed description of the item.")
    category: str = Field(..., title="Item Category", description="The category to which the item belongs.")
    price: float = Field(..., title="Price", description="The price of the item.")
    location: Optional[str] = Field(None, title="Location", description="The location where the item is available.")


class ItemView(BaseModel):
    id: int = Field(..., title="Item ID", description="The unique identifier for the item.")
    title: str = Field(..., title="Item Title", description="The title of the item.")
    description: str = Field(..., title="Item Description", description="A detailed description of the item.")
    category: str = Field(..., title="Item Category", description="The category of the item.")
    price: float = Field(..., title="Price", description="The price of the item.")
    location: Optional[str] = Field(None, title="Location", description="The location where the item is available.")
    created_at: datetime = Field(..., title="Creation Date", description="The date and time when the item was created.")

    class Config:
        orm_mode = True


class ItemFilter(BaseModel):
    category: Optional[str] = Field(None, title="Category", description="Filter items by category.")
    min_price: Optional[float] = Field(None, title="Minimum Price", description="Filter items with price greater than or equal to this value.")
    max_price: Optional[float] = Field(None, title="Maximum Price", description="Filter items with price less than or equal to this value.")
    location: Optional[str] = Field(None, title="Location", description="Filter items by location.")
    search: Optional[str] = Field(None, title="Search", description="Search items by title or description.")


class Pagination(BaseModel):
    page: int = Field(1, ge=1, title="Page", description="The page number for paginated results.")
    size: int = Field(10, ge=1, title="Size", description="The number of items per page.")


# TOKEN SCHEMAS
class Token(BaseModel):
    access_token: str = Field(..., title="Access Token", description="The access token issued for authentication.")
    token_type: str = Field(..., title="Token Type", description="The type of token, usually 'bearer'.")


class TokenData(BaseModel):
    id: int = Field(..., title="User ID", description="The unique identifier for the user associated with the token.")


# CHAT
class ChatMessage(BaseModel):
    sender_id: int = Field(..., title="Sender ID", description="The ID of the user sending the message.")
    recipient_id: int = Field(..., title="Recipient ID", description="The ID of the user receiving the message.")
    content: str = Field(..., title="Message Content", description="The content of the chat message.")
    timestamp: datetime = Field(..., title="Timestamp", description="The date and time when the message was sent.")

    class Config:
        orm_mode = True


class ChatSummary(BaseModel):
    partner_id: int = Field(..., title="Partner ID", description="The ID of the user with whom the chat was held.")
    last_message: str = Field(..., title="Last Message", description="The content of the last message in the chat.")
    timestamp: datetime = Field(..., title="Timestamp", description="The date and time when the last message was sent.")
