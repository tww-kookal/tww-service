from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from datetime import timedelta
from ..config import config
from pydantic import BaseModel
import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from .. import auth
from ..biz import adminHelper as helper, usersHelper as userHelper

from .. import utils

######## Logging ########
logger = logging.getLogger("tww.service.admin")

router = APIRouter()
#     prefix="/",  # all routes start with /api/v1/rooms
#     tags=["Admin"]    # OpenAPI grouping
# )

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


class ScriptModel (BaseModel):
    query: str

@router.post("/execute")
async def execute(query: ScriptModel, authorized_user: dict = Depends(auth.authorizedUser(['admin']))):
    try:
        createdRoom = helper.execute(query.model_dump())
        return {
            "status": status.HTTP_200_OK,
            "message": "Success"
        }

    except Exception as e:
        logger.error (f"Exception in Execute: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to execute the string")
