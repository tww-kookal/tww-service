from datetime import datetime, timedelta
from jose import jwt
import logging
from passlib.context import CryptContext
from .config.config import settings
from .data.usersDB import queryRolesForUserDB

####### Logger ############
logger = logging.getLogger("tww.service.utils")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#pwd_context = CryptContext(schemes=["bcrypt"],bcrypt__ident="2b", deprecated="auto")
print(pwd_context.hash("@dmini$Tr@T0r@Tww#112"))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.info(f"Password Match: {pwd_context.verify(plain_password, hashed_password)}")
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def isAuthorized(userName: str, authorizedRoles: list):
    #Connect to to database and get all the roles for this user
    userRoles = queryRolesForUserDB(userName)
    logger.debug(f"Roles for the User: {userRoles}")
    logger.debug(f"Roles Expected User: {authorizedRoles}")
    if userRoles is None:
        userRoles = []
    userRoles.append('self')
    
    # check for either of the authorized roles is in the user roles
    for role in userRoles:
        if role in authorizedRoles:
            return True
    return False

