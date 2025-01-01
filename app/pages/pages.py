from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=['Pages'])

@router.get('/login', response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get('/register', response_class=HTMLResponse)
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get('/inbox', response_class=HTMLResponse)
def get_chats_page(request: Request, current_user: int = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("chats.html", {"request": request})

@router.get('/inbox/chat/{chat_id}', response_class=HTMLResponse)
def get_chat_page(chat_id: str, request: Request, current_user: int = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse(
        "chat.html", 
        {"request": request, "chat_id": chat_id, "user": current_user}
    )

@router.get('/', response_class=HTMLResponse)
def get_index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get('/create_item', response_class=HTMLResponse)
def get_create_item_page(request: Request, current_user: int = Depends(oauth2.get_current_user)):
    return templates.TemplateResponse("create_item.html", {"request": request})

