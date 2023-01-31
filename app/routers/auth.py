from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session

from .. import database, utils, schemas, models


router = APIRouter(tags=["authentication"])


@router.post("/login")
async def login(
    user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
        )

    return {"token": "ablubabdadba"}
