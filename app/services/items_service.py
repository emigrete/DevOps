import newrelic.agent
from sqlalchemy.orm import Session
from app.db.item_model import Item
from app.models.schemas import ItemCreate


# function_trace en cada operación → la traza muestra la capa service
# envolviendo el span de datastore (SQL) que el agente captura automáticamente.
@newrelic.agent.function_trace()
def create_item(db: Session, data: ItemCreate) -> Item:
    item = Item(name=data.name, description=data.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@newrelic.agent.function_trace()
def list_items(db: Session) -> list[Item]:
    return db.query(Item).all()


@newrelic.agent.function_trace()
def get_item(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


@newrelic.agent.function_trace()
def delete_item(db: Session, item_id: int) -> bool:
    item = get_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
