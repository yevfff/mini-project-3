from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .api import user, auth, items, chat
from .pages import pages


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(chat.router)

# Frontend pages
app.include_router(pages.router)

@app.get("/")
def root():
    return {"message": "Exchange your stuff"}

