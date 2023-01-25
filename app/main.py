from fastapi import FastAPI, Depends, status, HTTPException, Response

from sqlalchemy.orm import Session
from .database import get_db, engine

from typing import List

from . import models, schemas, utils

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# POST


@app.get("/posts", response_model=List[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()

    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):

    new_post = models.Post(**post.dict())

    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )

    db.add(new_post)  # Add
    db.commit()  # Commit
    db.refresh(new_post)  # Return the new created post.

    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db)):

    post_on_db = db.query(models.Post).filter(models.Post.id == id).first()

    if not post_on_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    return post_on_db


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
async def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post_on_db = post_query.first()

    if post_on_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    post_updated = post_query.first()

    return post_updated


# USER


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)

    user.password = hashed_password
    new_user = models.User(**user.dict())

    db.add(new_user)  # Add
    db.commit()  # Commit
    db.refresh(new_user)  # Return the new created post.

    return new_user


@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} not found.",
        )

    return user
