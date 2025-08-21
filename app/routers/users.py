from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
import traceback
from typing import List
from pydantic import BaseModel

from ..biz import usersHelper as helper
from ..data.usersDB import queryUserByIdDB, queryAllUsersDB, queryUserDB, assignRolesToUserDB
from ..config.config import settings
from .. import auth

####### Logger ############
logger = logging.getLogger("tww.service.users")

router = APIRouter(
    prefix="/api/v1/users",  # all routes start with /api/v1/users
    tags=["Users"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

######## Curl API Sample ##########
# curl -X POST "http://localhost:8000/createUser" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
#      -H "Content-Type: application/json" \
#      -d '{"username":"newuser", "password":"password123", "role_id":1}'
#####################

class UserBaseModel (BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    booking_commission: int

class UserModel (UserBaseModel):
    password: str

class UerDetailModel (BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    booking_commission: int
    
class TokenRequest(BaseModel):
    token: str    

@router.post("/googleAuth/signup")
async def googleSignup(tokenrequest: TokenRequest):
    try:
        userInfo = auth.getUserDetailsFromAccessToken(tokenrequest.token)
        createdUser = helper.createUser(userInfo)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User created successfully",
            "user": createdUser
        }
    except helper.DuplicateUserException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        traceback.print_stack()
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Unable to create user, check logs"
        )

@router.post("/googleAuth/login")
async def googleLogin(tokenrequest: TokenRequest):
    try:
        logger.debug(f"GoogleLogin::Token Request: {tokenrequest}")

        userInfo = auth.getUserDetailsFromAccessToken(tokenrequest.token)

        userDetails = helper.getUserByUserName(userInfo["username"])

        userRoles = helper.getRolesForUser(userInfo["username"])

        return {
            "status": status.HTTP_200_OK,
            "user": {
                "user_id": userDetails["user_id"], 
                "username": userDetails["username"], 
                "email": userDetails["email"], 
                "name": userInfo["first_name"] + " " + userInfo["last_name"], 
                "first_name": userInfo['first_name'], 
                'last_name': userInfo['last_name'],
                "roles": userRoles
            }
        }
    except helper.UserNotAvailableException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Unable to create user, check logs"
        )

@router.post("/auth/google")
async def auth_google(data: TokenRequest):
    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            data.token, requests.Request(), settings.GOOGLE_APP_CLIENT_ID
        )

        # Extract user info
        userid = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name")

        return {"userid": userid, "email": email, "name": name}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
@router.get("/")
async def list(authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    users = queryAllUsersDB()
    return {
        "status": status.HTTP_200_OK,
        "message": "Users listed successfully",
        "total": len(users),
        "users": users
    } 

@router.post("/create")
async def create(user: UserModel, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
    try:
        createdUser = helper.createUser(user.dict())
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User created successfully",
            "user": createdUser
        }
    except helper.DuplicateUserException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Unable to create user, check logs"
        )

@router.post("/update")
async def update(user: UerDetailModel, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
    try:
        logger.debug("UserAPI::update::user: %s", user.dict())
        updatedUser = helper.updateUserDetail(user.dict())
        return {
            "status": status.HTTP_200_OK,
            "message": "User updated successfully",
            "user": updatedUser
        }
    except helper.UserNotAvailableException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Unable to create user, check logs"
        )


@router.get("/getById/{user_id}")
async def getById(user_id: int, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can get other users' information"
        )
    user = queryUserByIdDB(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "status": status.HTTP_200_OK,
        "user": user
    }

@router.get("/getByUsername/{username}")
async def getByUsername(username: str, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can get other users' information"
        )
    user = queryUserDB(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "status": status.HTTP_200_OK,
        "user": user
    }  

@router.post("/assignRolesToUser")
async def assignRolesToUser(username: str, role_names: List[str],authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )   
    try:
        assignRolesToUserDB(username, role_names)
        return {
            "status": status.HTTP_200_OK,
            "message": "Roles assigned to user successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= "Roles are not assigned to the user, check logs"
        )

@router.get("/userRoles")
async def userRoles(username: str, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )   
    try:
        userRoles = helper.getRolesForUser(username)
        return {
            "status": status.HTTP_200_OK,
            "user": {
                "username": username,
                "roles": userRoles
            } 
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= "Roles are not assigned to the user, check logs"
        )

@router.get("/listMyRoles")
async def listMyRoles(authorized_user: dict = Depends(auth.authorizedUser(["self"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )   
    try:
        # userRoles = queryRolesForUserDB(current_user)
        return {
            "status": status.HTTP_200_OK,
            "user": {
                "username": authorized_user['user_name'],
                "roles": authorized_user['roles']
            } 
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= "Roles are not assigned to the user, check logs"
        )
