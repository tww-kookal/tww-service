from .. import utils 
from ..data import usersDB as userDB
import traceback
import logging
from .BizExceptions import DuplicateUserException, UserNotAvailableException

####### Logger ############
logger = logging.getLogger("tww.service.usershelper")

def validateUser(user, password: str):
    if not user or not utils.verify_password(password, user["password"]):
        return False
    return True

def queryUser(username: str):
    return userDB.queryUserDB(username)

def createUser(user: dict):
    if queryUser(user["username"]):
        raise DuplicateUserException(message="Username already registered")

    if "password" not in user:
        user["password"] = "password@123"

    if "booking_commission" not in user:
        user["booking_commission"] = 0.0

    user["hashed_password"] = utils.hash_password(user["password"])
    return userDB.persistUserDB(user)

def updateUserDetail(user: dict):
    logger.debug(f"UpdateUserDetail:: Query User {user}")
    userFound = userDB.queryUserByIdDB(user["user_id"])
    #if the userFound is not availble then raise an exception

    if not userFound:
        raise UserNotAvailableException(message = "User not available")

    if "booking_commission" not in user:
        user["booking_commission"] = 0.0

    logger.debug(f"Updating user detail: {user}")
    return userDB.updateUserDetailDB(user)

def getUserByID(user_id: str, throw_exception=True):
    user = userDB.queryUserByIdDB(user_id)
    if not user:
        logger.error(f"User not found")
        if throw_exception:
            raise UserNotAvailableException()
        else:
            return None
    return user

def getUserByUserName(username: str, throw_exception=True):
    user = userDB.queryUserDB(username)
    if not user:
        logger.error(f"User not found")
        if throw_exception:
            raise UserNotAvailableException()
        else:
            return None
    return user

def getFullNameOfUserByID(user_id: int):
    user_details = getUserByID(user_id, throw_exception=False)
    logger.info(f"User Full Name of User By ID {user_id} Details: {user_details}")
    if user_details:
        return user_details["first_name"] + " " + user_details['last_name']
    else:
        return ''

def getRolesForUser(user_name: int):
    return userDB.queryRolesForUserDB(user_name)

def getBookingSources():
    try:
        return userDB.queryAllBookingSourcesDB()
    except Exception as e:
        logger.error(f"Exception in getBookingSources: {e}")
        traceback.print_exc()
        raise e
