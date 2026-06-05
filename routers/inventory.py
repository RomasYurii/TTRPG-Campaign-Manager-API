from fastapi import APIRouter, HTTPException, status, Depends, Header
from database import schemas
from database.database import get_db, Session
from database import models
from security import get_current_user

router = APIRouter()


@router.post("/characters/{character_id}/inventory", status_code=status.HTTP_201_CREATED)
def add_item_to_inventory(
        character_id: int,
        item_data: schemas.InventoryAdd,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_char = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_char is None:
        raise HTTPException(status_code=404, detail="Character not found")

    if current_user.id != db_char.player_id and current_user.role != "dm":
        raise HTTPException(status_code=403, detail="Not allowed to edit this inventory")

    db_item = db.query(models.Item).filter(models.Item.id == item_data.item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found in database")

    inv_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.item_id == item_data.item_id,
        models.InventoryItem.character_id == character_id
    ).first()

    if inv_item:
        inv_item.quantity += item_data.quantity
    else:
        new_item = models.InventoryItem(
            item_id=item_data.item_id,
            character_id=character_id,
            quantity=item_data.quantity
        )
        db.add(new_item)

    db.commit()

    return {"message": "Item successfully added to character", "character": db_char.name}


@router.get("/characters/{character_id}/inventory")
def list_inventory(
        character_id: int,
        accept_language: str = Header(default="en"),
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_char = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_char is None:
        raise HTTPException(status_code=404, detail="Character not found")

    if current_user.id != db_char.player_id and current_user.role != "dm":
        raise HTTPException(status_code=403, detail="Not allowed to view this inventory")

    inventory_items = db.query(models.InventoryItem).filter(models.InventoryItem.character_id == character_id).all()

    result = []
    for inv in inventory_items:
        actual_item = inv.item

        if "uk" in accept_language:
            localized_name = actual_item.name_uk
        else:
            localized_name = actual_item.name_en

        result.append({
            "name": localized_name,
            "quantity": inv.quantity,
            "rarity": actual_item.rarity
        })

    return result