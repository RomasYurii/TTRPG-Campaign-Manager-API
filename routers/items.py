from fastapi import APIRouter, Depends, Header
from database.database import get_db, Session
from database import models
from database.schemas import ItemResponse
router = APIRouter()

@router.get("/items", response_model=list[ItemResponse])
def list_items( limit: int = 10,
                offset: int = 0,
                accept_language: str = Header(default="en"),
                db: Session = Depends(get_db)
):
    result = []
    db_items = db.query(models.Item).limit(limit).offset(offset).all()

    for item in db_items:
        if "uk" in accept_language:
            localized_name = item.name_uk
            localized_desc = item.description_uk
        else:
            localized_name = item.name_en
            localized_desc = item.description_en


        item_data = {
            "id": item.id,
            "name": localized_name,
            "description": localized_desc,
            "rarity": item.rarity,
            "price": item.price
        }

        # Ми просто додаємо словник у список. FastAPI сам пропустить його
        # через схему ItemResponse (завдяки response_model у декораторі).
        result.append(item_data)

    return result
