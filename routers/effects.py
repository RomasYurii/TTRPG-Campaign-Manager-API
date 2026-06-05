from fastapi import APIRouter, HTTPException, status, Depends, Header
from database import schemas
from database.database import get_db, Session
from database import models
from security import get_current_user

router = APIRouter()

@router.post("/characters/{character_id}/effects", status_code=status.HTTP_201_CREATED)
def add_effect_on_character(
        character_id: int,
        effect: schemas.EffectAdd,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_char = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_char is None:
        raise HTTPException(status_code=404, detail="Character not found")

    if current_user.role != "dm":
        raise HTTPException(status_code=403, detail="Only DMs can add effects")

    db_effect = db.query(models.StatusEffect).filter(models.StatusEffect.id == effect.effect_id).first()
    if db_effect is None:
        raise HTTPException(status_code=404, detail="Effect not found in database")

    existing_effect = db.query(models.CharacterEffect).filter(
        models.CharacterEffect.character_id == character_id,
        models.CharacterEffect.effect_id == effect.effect_id
    ).first()

    if existing_effect is None:
        new_effect = models.CharacterEffect(
            character_id=character_id,
            effect_id=effect.effect_id
        )
        db.add(new_effect)
        db.commit()
        db.refresh(new_effect)
        return {"message": "Effect successfully added to character", "Character": db_char.name}
    else:
        raise HTTPException(status_code=400, detail="Effect already active")


@router.get("/characters/{character_id}/effects")
def list_effects(
        character_id: int,
        accept_language: str = Header(default="en"),
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_char = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_char is None:
        raise HTTPException(status_code=404, detail="Character not found")

    if current_user.id != db_char.player_id and current_user.role != "dm":
        raise HTTPException(status_code=403, detail="Not allowed to view these effects")

    character_effects = db.query(models.CharacterEffect).filter(models.CharacterEffect.character_id == character_id).all()

    result = []
    for char_effect in character_effects:
        actual_effect = char_effect.effect

        if "uk" in accept_language:
            localized_name = actual_effect.name_uk
            localized_description = actual_effect.description_uk
        else:
            localized_name = actual_effect.name_en
            localized_description = actual_effect.description_en

        result.append({
            "name": localized_name,
            "description": localized_description,
            "is_positive": actual_effect.is_positive
        })

    return result