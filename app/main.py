from fastapi import FastAPI, Depends, status, HTTPException, Response

from sqlalchemy.orm import Session
from .database import get_db, engine

from pydantic import BaseModel

from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()

    return {"data": posts}


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, db: Session = Depends(get_db)):

    new_post = models.Post(**post.dict())

    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )

    db.add(new_post)  # Add
    db.commit()  # Commit
    db.refresh(new_post)  # Return the new created post.

    return {"data": new_post}


@app.get("/posts/{id}")
async def get_post(id: int, db: Session = Depends(get_db)):

    post_on_db = db.query(models.Post).filter(models.Post.id == id).first()

    if not post_on_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    return {"data": post_on_db}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, post: Post, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post_on_db = post_query.first()

    if post_on_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    post_updated = post_query.first()

    return {"data": post_updated}
