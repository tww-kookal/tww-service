from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..biz import usersHelper as helper
import logging
from ..data import database
from ..data.usersDB import queryUserByIdDB, queryAllUsersDB, queryUserDB, assignRolesToUserDB, queryRolesForUserDB
from typing import List
from pydantic import BaseModel

from .. import utils
from ..auth import get_current_user
from ..utils import isAuthorized

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

@router.post("/create")
async def create(user: UserModel, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
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
async def update(user: UerDetailModel, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
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
async def getById(user_id: int, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
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
async def getByUsername(username: str, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
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

@router.get("/")
async def list(current_user: dict = Depends(get_current_user)):
    logger.info(f"Current User: {current_user}")
    # Check if current user is admin    
    if isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can list all users"
        )

    users = queryAllUsersDB()
    return {
        "status": status.HTTP_200_OK,
        "message": "Users listed successfully",
        "total": len(users),
        "users": users
    }

@router.post("/assignRolesToUser")
async def assignRolesToUser(username: str, role_names: List[str], current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
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
async def userRoles(username: str, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )   
    try:
        userRoles = queryRolesForUserDB(username)
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
async def listMyRoles(current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["self"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )   
    try:
        userRoles = queryRolesForUserDB(current_user)
        return {
            "status": status.HTTP_200_OK,
            "user": {
                "username": current_user,
                "roles": userRoles
            } 
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail= "Roles are not assigned to the user, check logs"
        )
