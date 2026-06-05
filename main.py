from fastapi import FastAPI
from database import models
from database.database import engine, get_db, SessionLocal
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from security import verify_password, create_access_token
from database.models import User

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title = "DnD API",
    description="API service for DnD project",
    version="1.0"
)


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    # 1. Шукаємо користувача в БД
    user = db.query(User).filter(User.username == form_data.username).first()

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
