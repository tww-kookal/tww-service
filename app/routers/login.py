from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import logging
from datetime import timedelta
from .. import utils 
from ..config import config
from ..biz import usersHelper as userHelper


router = APIRouter(
    prefix="/api/v1",  # all routes start with /api/v1
    tags=["Login"]    # OpenAPI grouping
)

####### Logger ############
logger = logging.getLogger("tww.service.login")

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
