from fastapi import APIRouter, HTTPException, status, Depends
from database import schemas
from database.database import get_db, SessionLocal
from database import models
from security import create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    # 1. Шукаємо користувача в БД
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 2. Якщо користувача немає або пароль не збігається — кидаємо помилку 401
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Якщо все ок, генеруємо токен
    access_token = create_access_token(data={"sub": user.username})

    # 4. Повертаємо токен у форматі, якого вимагають тести та стандарт OAuth2
    return {"access_token": access_token, "token_type": "bearer"}