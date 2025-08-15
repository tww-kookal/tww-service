from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Annotated
from datetime import timedelta
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date
from ..auth import get_current_user
from ..biz import adminHelper as helper, usersHelper as userHelper

from .. import utils

######## Logging ########
logger = logging.getLogger("tww.service.admin")

router = APIRouter(
    prefix="/api/v1/admin",  # all routes start with /api/v1/rooms
    tags=["Admin"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = userHelper.queryUser(form_data.username)

    if not userHelper.validateUser(user, form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = utils.create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/execute")
async def execute(string: str, current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        createdRoom = helper.execute(string)
        return {
            "status": status.HTTP_200_OK,
            "message": "Success"
        }

    except Exception as e:
        logger.error (f"Exception in Execute: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to execute the string")
