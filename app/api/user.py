from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from typing import List

router = APIRouter(
    prefix="/api/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Створення нового користувача.

    - email: Електронна пошта користувача (унікальна).
    - username: Ім'я користувача у форматі @username (унікальне).
    - password: Пароль користувача (зберігається в хешованому вигляді).
    """
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/search", response_model=List[schemas.UserOut])
def search_users(username: str, db: Session = Depends(get_db)):
    """
    Search users by username.
    Returns a list of users matching the given username.
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username query parameter is required")
    
    users = db.query(models.User).filter(models.User.username.ilike(f"%{username}%")).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    
    return users

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    """
    Отримання інформації про користувача за ID.

    - **id: Унікальний ідентифікатор користувача.
    - Якщо користувача не знайдено, повертається статус 404.
    """
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    return user
