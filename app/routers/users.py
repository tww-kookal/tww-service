from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
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
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
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
    user_type: str

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
    user_type: str
    
class TokenRequest(BaseModel):
    token: str    

@router.post("/googleAuth/signup")
@limiter.limit("10/second")
async def googleSignup(request: Request, tokenrequest: TokenRequest):
    try:
        userInfo = auth.getUserDetailsFromAccessToken(tokenrequest.token)
        if "user_type" not in userInfo:
            userInfo["user_type"] = "CUSTOMER"
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
@limiter.limit("10/second")
async def googleLogin(request: Request, tokenrequest: TokenRequest):
    try:
        logger.debug(f"GoogleLogin::Token Request: ")

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
@limiter.limit("10/second")
async def auth_google(request: Request, data: TokenRequest):
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
@limiter.limit("10/second")
async def list(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    users = queryAllUsersDB()
    return {
        "status": status.HTTP_200_OK,
        "message": "Users listed successfully",
        "total": len(users),
        "users": users
    } 

@router.get("/bookingSource")
@limiter.limit("10/second")
async def list_booking_sources(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin", "manager"])) ):
    users = helper.getBookingSources()
    return {
        "status": status.HTTP_200_OK,
        "message": "Booking Sources listed successfully",
        "users": users
    } 

@router.get("/employees")
@limiter.limit("10/second")
async def list_employees(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin", "manager"])) ):
    users = helper.getEmployees()
    return {
        "status": status.HTTP_200_OK,
        "message": "Employees listed successfully",
        "users": users
    } 

@router.get("/vendors")
@limiter.limit("10/second")
async def list_vendors(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin", "manager"])) ):
    users = helper.getVendors()
    return {
        "status": status.HTTP_200_OK,
        "message": "Vendors listed successfully",
        "users": users
    } 

@router.post("/create")
@limiter.limit("10/second")
async def create(request: Request, user: UserModel, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
    try:
        request = user.model_dump()
        first_name = request["first_name"]
        last_name = request["last_name"]
        request["username"] = f"{first_name.lower()}_{last_name.lower()}_{request['phone'][:5]}"
        createdUser = helper.createUser(request)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User created successfully",
            "user": createdUser
        }
    except helper.DuplicateUserException as e:
        logger.error("DuplicateUserException creating user: %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        logger.error("Exception creating user: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user, check logs"
        )

@router.post("/update")
@limiter.limit("10/second")
async def update(request: Request, user: UerDetailModel, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
    # Check if current user is admin
    if authorized_user['is_authorized'] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
    try:
        logger.debug("UserAPI::update::user: %s", user.model_dump())
        updatedUser = helper.updateUserDetail(user.model_dump())
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
@limiter.limit("10/second")
async def getById(request: Request, user_id: int, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
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
@limiter.limit("10/second")
async def getByUsername(request: Request, username: str, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
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
@limiter.limit("10/second")
async def assignRolesToUser(request: Request, username: str, role_names: List[str],authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
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
@limiter.limit("10/second")
async def userRoles(request: Request, username: str, authorized_user: dict = Depends(auth.authorizedUser(["admin"])) ):
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
@limiter.limit("10/second")
async def listMyRoles(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["self"])) ):
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
