from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging
from jose import jwt, JWTError
from .config.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
logger = logging.getLogger("tww.service.auth")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        logger.info(f"Logged In User: {username}")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
