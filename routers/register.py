from fastapi import APIRouter, HTTPException, status, Depends
from database import schemas
from database.database import get_db, SessionLocal
from database import models
from security import get_password_hash

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: SessionLocal = Depends(get_db)):
    # 1. Перевіряємо, чи немає вже такого юзера
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # 2. Хешуємо пароль і зберігаємо
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "username": new_user.username}