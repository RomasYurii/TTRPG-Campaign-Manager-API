from fastapi import APIRouter, HTTPException,status, Depends, BackgroundTasks
from database import schemas
from database.database import get_db, Session
from database import models
from security import get_current_user
import time


def send_notification_email(dm_email: str, campaign_title: str, character_name: str):
    """
    Ця функція виконується у фоні. Вона імітує відправку листа.
    """
    print(f"[BACKGROUND TASK] Починаємо відправку листа на {dm_email}...")

    # Імітуємо затримку мережі (наприклад, 3 секунди сервер намагається відправити лист)
    time.sleep(15)

    print(
        f"[BACKGROUND TASK] Лист успішно надіслано! Текст: В кампанію '{campaign_title}' приєднався герой '{character_name}'.")
router = APIRouter()


@router.post("/characters", status_code=status.HTTP_201_CREATED)
def create_character(
        character: schemas.CharacterCreate,
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)):

    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == character.campaign_id).first()
    if db_campaign is None:
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

    dm_user = db.query(models.User).filter(models.User.id == db_campaign.dm_id).first()

    if dm_user and dm_user.email:
        # ДОДАЄМО ЗАДАЧУ В ЧЕРГУ ФОНОВИХ ЗАВДАНЬ
        # Першим аргументом передаємо саму функцію (без дужок!), а далі — всі її параметри
        background_tasks.add_task(
            send_notification_email,
            dm_user.email,
            db_campaign.title,
            new_character.name
        )

    return {"message": "Character created successfully", "Character": character.name}


@router.get("/characters")
def list_characters( current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Character).filter(models.Character.player_id == current_user.id).all()
