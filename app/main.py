from fastapi import FastAPI
from . import models
from .database import engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Hello World pushing out to ubuntu"}