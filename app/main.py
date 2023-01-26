from fastapi import FastAPI

from .database import engine

from . import models
from .routers import user, post

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)

app.include_router(post.router)
