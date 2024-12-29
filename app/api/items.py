from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, oauth2
import os
from uuid import uuid4

router = APIRouter(
    prefix="/api/items",
    tags=["Items"]
)

UPLOAD_FOLDER = "uploads/items_photos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.get("/", response_model=List[schemas.ItemView], status_code=status.HTTP_200_OK)
def get_items(
        filter_params: schemas.ItemFilter = Depends(),
        pagination: schemas.Pagination = Depends(),
        db: Session = Depends(get_db)
):
    """
    Отримати список товарів за фільтрами (категорія, ціна, місцезнаходження тощо) та пагінацією.

    **Response**
    - Список товарів, що відповідають фільтрам.
    """
    query = db.query(models.Item)

    if filter_params.category:
        query = query.filter(models.Item.category == filter_params.category)
    if filter_params.min_price is not None:
        query = query.filter(models.Item.price >= filter_params.min_price)
    if filter_params.max_price is not None:
        query = query.filter(models.Item.price <= filter_params.max_price)
    if filter_params.location:
        query = query.filter(models.Item.location == filter_params.location)
    if filter_params.search:
        query = query.filter(models.Item.title.contains(filter_params.search))

    items = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

    if not items:
        raise HTTPException(status_code=404, detail="No items found")

    return items


@router.post("/", response_model=schemas.ItemView, status_code=status.HTTP_201_CREATED)
def create_item(
        title: str = Form(...),
        description: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        location: str = Form(...),
        photo: Optional[UploadFile] = None,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user)
):
    """
    Створення нового товару з можливістю завантаження фото.

    **Request Body**
    - **title**: Назва товару.
    - **description**: Опис товару.
    - **category**: Категорія товару.
    - **price**: Ціна товару.
    - **location**: Місцезнаходження товару.
    - **photo**: Фото товару (не обов'язково).
    """
    file_path = None

    if photo:
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image")

        filename = f"{uuid4()}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(photo.file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    new_item = models.Item(
        title=title,
        description=description,
        category=category,
        price=price,
        location=location,
        user_id=current_user.id,
        photo_path=file_path
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# @router.post("/", response_model=schemas.ItemView, status_code=status.HTTP_201_CREATED)
# def create_item1(
#         item: schemas.ItemCreate,
#         photo: Optional[UploadFile] = None,
#         db: Session = Depends(get_db),
#         current_user: int = Depends(oauth2.get_current_user)
# ):
#     """
#     Створення нового товару з використанням схеми для товару та можливістю завантаження фото.
#
#     **Request Body**
#     - **item**: Інформація про товар, включаючи його атрибути.
#     - **photo**: Фото товару (не обов'язково).
#
#     **Response**
#     - Створений товар з інформацією про нього.
#
#
#     """
#     file_path = None
#
#     if photo:
#         if not photo.content_type.startswith("image/"):
#             raise HTTPException(status_code=400, detail="Uploaded file must be an image")
#
#         filename = f"{uuid4()}.jpg"
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         try:
#             with open(file_path, "wb") as f:
#                 f.write(photo.file.read())
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
#
#     new_item = models.Item(
#         title=item.title,
#         description=item.description,
#         category=item.category,
#         price=item.price,
#         location=item.location,
#         user_id=current_user.id,
#         photo_path=file_path
#     )
#     db.add(new_item)
#     db.commit()
#     db.refresh(new_item)
#
#     return new_item
