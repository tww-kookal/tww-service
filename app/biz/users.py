from .. import utils 
from ..data.usersDB import queryUserDB
import logging
####### Logger ############
logger = logging.getLogger("tww.service.usershelper")

def validateUser(user, password: str):
    if not user or not utils.verify_password(password, user["password"]):
        return False
    return True

def queryUser(username: str):
    return queryUserDB(username)