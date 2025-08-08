from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .. import utils 
from ..config import config
from ..biz.users import validateUser, queryUser

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = queryUser(form_data.username)

    if not validateUser(user, form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = utils.create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
