from fastapi import FastAPI
from . import models
from .database import engine
from .routers import user, auth

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World pushing out to ubuntu"}


