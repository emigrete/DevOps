from sqlalchemy.orm import Session
from app.db.item_model import Item
from app.models.schemas import ItemCreate


def create_item(db: Session, data: ItemCreate) -> Item:
    item = Item(name=data.name, description=data.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(db: Session) -> list[Item]:
    return db.query(Item).all()


def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


def delete_item(db: Session, item_id: int) -> bool:
    item = get_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
