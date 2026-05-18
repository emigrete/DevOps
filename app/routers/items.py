from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import ItemCreate, ItemOut
from app.services import items_service

router = APIRouter(prefix="/items")


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return items_service.list_items(db)


@router.post("", response_model=ItemOut, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    return items_service.create_item(db, data)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = items_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    if not items_service.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
