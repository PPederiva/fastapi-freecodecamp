from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import database, models, schemas
from .config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_schema), db: Session = Depends(database.get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validade credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(
        token=token, credentials_exception=credentials_exception
    )

    user_id = db.query(models.User).filter(
        models.User.id == token_data.id).first()

    return user_id


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=user_id)

    except JWTError as exc:
        raise credentials_exception from exc

    return token_data
