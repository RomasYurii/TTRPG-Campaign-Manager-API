from fastapi import FastAPI
from database import models
from database.database import engine
from fastapi import Depends
from security import get_current_user
from routers import register, login, campaigns, characters, items, inventory, effects
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from security import limiter # Імпортуємо наш лімітер
models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title = "DnD API",
    description="API service for DnD project",
    version="1.0",
    root_path= "/api/v1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(register.router, tags=["Authentication"])
app.include_router(login.router, tags=["Login"])
app.include_router(campaigns.router, tags=["Campaigns"])
app.include_router(characters.router, tags=["Characters"])
app.include_router(items.router, tags=["Items"])
app.include_router(inventory.router, tags=["Inventory"])
app.include_router(effects.router, tags=["Effects"])

@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

