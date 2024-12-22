from fastapi import FastAPI, Depends, HTTPException, Query, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..database import get_db
from .. import models

router = APIRouter(
    prefix="/ads",
    tags=["Advertisements"]
)


@router.get("/", response_model=List[dict])  # Response модель условно представлена как dict
def get_ads(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Filter by minimum price"),
    max_price: Optional[float] = Query(None, description="Filter by maximum price"),
    limit: int = Query(10, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    db: Session = Depends(get_db)
):


    query = db.query(models.Ad)


    if category:
        query = query.filter(models.Ad.category == category)
    if min_price is not None:
        query = query.filter(models.Ad.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Ad.price <= max_price)


    ads = query.offset(offset).limit(limit).all()

    if not ads:
        raise HTTPException(status_code=404, detail="No advertisements found")


    return [{"id": ad.id, "title": ad.title, "price": ad.price, "category": ad.category} for ad in ads]
