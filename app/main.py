from fastapi import FastAPI
from . import models
from .database import engine
from .routers import user, auth, two

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(two.router)

@app.get("/")
def root():
    return {"message": "Exchange your stuff"}
