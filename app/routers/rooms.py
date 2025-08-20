from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Annotated
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import date
from .. import auth
from ..biz import roomsHelper as helper
from .. import utils

######## Logging ########
logger = logging.getLogger("tww.service.rooms")

router = APIRouter(
    prefix="/api/v1/rooms",  # all routes start with /api/v1/rooms
    tags=["Rooms"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

class RoomModel (BaseModel):
    room_id: int
    room_name: str
    min_capacity: int
    max_capacity: int
    number_of_beds: int
    number_of_bathrooms: int

@router.get("/", response_model= None)
async def listRooms(authorized_user: dict = Depends(auth.authorizedUser(["self"]))):
    rooms = helper.getAllRooms()
    return {
        "status": status.HTTP_200_OK,
        "rooms": rooms
    }

@router.get("/byName/{room_name}", response_model= None)
async def getRoomByName(room_name: str, authorized_user: dict = Depends(auth.authorizedUser(["self"]))):
    room = helper.getRoomByName(room_name)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return {
        "status": status.HTTP_200_OK,
        "room": room
    }

@router.post("/create")
async def createRoom(room: RoomModel, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    try:
        createdRoom = helper.createRoom(room.model_dump())
        return {
            "status": status.HTTP_200_OK,
            "message": "Room created successfully",
            "room": createdRoom
        }

    except Exception as e:
        logger.error (f"Exception in createRoom: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to create the room")

