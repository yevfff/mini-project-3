from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, oauth2
from pathlib import Path
from uuid import uuid4

router = APIRouter(
    prefix="/api/items",
    tags=["Items"]
)

UPLOAD_FOLDER = Path("uploads/items_photos")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

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
    Create a new item with the possibility to upload a photo.

    **Request Body**
    - **title**: Item title.
    - **description**: Item description.
    - **category**: Item category.
    - **price**: Item price.
    - **location**: Location where the item is located.
    - **photo**: Optional photo of the item.
    """
    file_path = None

    if photo:
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image")

        filename = f"{uuid4()}.jpg"
        file_path = UPLOAD_FOLDER / filename
        try:
            with file_path.open("wb") as f:
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
        photo_path=f"items_photos/{filename}" if file_path else None
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user)
):
    """
    Delete an item by its ID. Only the owner of the item can delete it.

    **Request Body**
    - **item_id**: ID of the item to be deleted.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this item")

    db.delete(item)
    db.commit()

    return {"detail": "Item deleted successfully"}
