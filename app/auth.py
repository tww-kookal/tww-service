from fastapi import HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests

import requests as http_req

from google.oauth2 import id_token as google_id_token
import logging
from jose import jwt, JWTError
from .config.config import settings
from .data import usersDB as userDB
from .biz import BizExceptions as biz

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
logger = logging.getLogger("tww.service.auth")

def getUserDetailsFromAccessToken(accessToken: str):
    try:
        userInfoResp = http_req.get("https://www.googleapis.com/oauth2/v3/userinfo", 
            headers = {'Authorization': f"Bearer {accessToken}"},
        )
        if userInfoResp.status_code == 200:
            user_info = userInfoResp.json()
            logger.debug(f"GetUserDetailsFromAccessToken::User Info: {user_info}")
            return {
                'username' : user_info["sub"],
                'email' : user_info["email"],
                'name' : user_info["name"],
                'first_name' : user_info['given_name'] or '',
                'last_name' : user_info['family_name'] or '',
                'phone': user_info.get('phone_number') or 'NO-PHONE',
                'picture': user_info.get('picture') or 'NO-PICTURE',
            }
        else:
            logger.error(f"GetUserDetailsFromAccessToken::Error: {userInfoResp.status_code}, {userInfoResp.text}")
            raise biz.UserNotAvailableException(message = "User not found in repository")
    except Exception as e:
        logger.error(f"GetUserDetailsFromAccessToken::Exception: {e}")
        raise e

def getUserDetailsFromIdToken(idToken: str):
    idinfo = google_id_token.verify_oauth2_token(
        idToken, requests.Request(), settings.GOOGLE_APP_CLIENT_ID  
    )

    # Extract user info
    userDetails = {
        'username' : idinfo["sub"],
        'email' : idinfo["email"],
        'name' : idinfo.get("name"),
        'first_name' : idinfo.get('given_name') or '',
        'last_name' : idinfo.get('family_name') or '',
        'phone' : idinfo.get('phone_number') or 'NO-PHONE',
        'picture': idinfo.get('picture') or 'NO-PICTURE',
    }
    logger.debug(f"GetUserDetailsFromIdToken::User Info: {userDetails['email']}")
    return userDetails

def authorizedUser(authorizedRoles: list):
    try:
        async def wrapper(authorization: str = Header(...)):            
            token = authorization.replace("Bearer ", "")

            userDetails = getUserDetailsFromAccessToken(token)
            # Check if the user is already registered
            userRoles = userDB.queryRolesForUserDB(userDetails["username"])
            logger.debug(f"Roles for the User: {userRoles}, Roles Expected : {authorizedRoles}")
            if userRoles is None:
                userRoles = []
            userRoles.append('self')
            
            # check for either of the authorized roles is in the user roles
            for role in userRoles:
                if role in authorizedRoles:
                    return {
                        'is_authorized': True,
                        'user_name': userDetails["username"],
                        'email': userDetails["email"],
                        'name': userDetails["name"],
                        'roles': userRoles,
                    }

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        return wrapper
    except HTTPException as e:  
        logger.error(f"HTTP Exception: {e}")
        raise e
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise e

