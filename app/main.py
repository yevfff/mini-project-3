from fastapi import FastAPI
from . import models
from .database import engine
from .routers import user, auth, items, chat

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Exchange your stuff"}
