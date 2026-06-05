from fastapi import FastAPI
from database import models
from database.database import engine
from fastapi import Depends
from security import get_current_user
from routers import register, login, campaigns, characters, items

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title = "DnD API",
    description="API service for DnD project",
    version="1.0",
    openapi_prefix= "/api/v1.0",
)

app.include_router(register.router, tags=["Authentication"])
app.include_router(login.router, tags=["Login"])
app.include_router(campaigns.router, tags=["Campaigns"])
app.include_router(characters.router, tags=["Characters"])
app.include_router(items.router, tags=["Items"])


@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

