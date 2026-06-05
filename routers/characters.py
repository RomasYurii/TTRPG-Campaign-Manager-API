from fastapi import APIRouter, HTTPException,status, Depends
from database import schemas
from database.database import get_db, Session
from database import models
from security import get_current_user

router = APIRouter()


@router.post("/characters", status_code=status.HTTP_201_CREATED)
def create_character(character: schemas.CharacterCreate, current_user: models.User = Depends(get_current_user) ,db: Session = Depends(get_db)):
    if db.query(models.Campaign).filter(character.campaign_id == models.Campaign.id).first() is None:
        raise HTTPException(status_code=404, detail="No Campaign found")


    new_character = models.Character(
        name=character.name,
        race=character.race,
        char_class=character.char_class,
        player_id = current_user.id,
        campaign_id= character.campaign_id
    )

    db.add(new_character)
    db.commit()
    db.refresh(new_character)


    return {"message": "Character created successfully", "Character": character.name}


@router.get("/characters")
def list_characters( current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Character).filter(models.Character.player_id == current_user.id).all()
