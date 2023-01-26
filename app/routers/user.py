from fastapi import FastAPI, Depends, status, HTTPException, Response, APIRouter

from sqlalchemy.orm import Session
from ..database import get_db

from typing import List

from .. import models, schemas, utils

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)

    user.password = hashed_password
    new_user = models.User(**user.dict())

    db.add(new_user)  # Add
    db.commit()  # Commit
    db.refresh(new_user)  # Return the new created post.

    return new_user


@router.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} not found.",
        )

    return user
