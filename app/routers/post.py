from fastapi import Depends, status, HTTPException, Response, APIRouter

from sqlalchemy.orm import Session
from ..database import get_db

from typing import List

from .. import models, schemas, oauth2

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.Post])
async def get_posts(
    db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)
):

    posts = db.query(models.Post).all()

    print(current_user.email)

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):

    new_post = models.Post(**post.dict())

    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )

    db.add(new_post)  # Add
    db.commit()  # Commit
    db.refresh(new_post)  # Return the new created post.

    return new_post


@router.get("/{id}", response_model=schemas.Post)
async def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):

    post_on_db = db.query(models.Post).filter(models.Post.id == id).first()

    if not post_on_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    return post_on_db


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

    post_query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
async def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):

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
