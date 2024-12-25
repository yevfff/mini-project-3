from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, oauth2
import os
from uuid import uuid4

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

UPLOAD_FOLDER = "uploads/items_photos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.get("/", response_model=List[schemas.ItemView])
def get_items(
    filter_params: schemas.ItemFilter = Depends(),
    pagination: schemas.Pagination = Depends(),
    db: Session = Depends(get_db)
):
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

    # Apply pagination
    items = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()

    if not items:
        raise HTTPException(status_code=404, detail="No items found")

    return items



@router.post("/", response_model=schemas.ItemView)
def create_item(
        title: str = Form(...),
        description: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        location: str = Form(...),
        photo: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
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

# @router.post("/", response_model=schemas.ItemView)
# def create_item(
#         item: schemas.ItemCreate,
#         photo: Optional[UploadFile] = File(None),
#         db: Session = Depends(get_db),
#         current_user: schemas.UserOut = Depends(oauth2.get_current_user)
# ):
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

