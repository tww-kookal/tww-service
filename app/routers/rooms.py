from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Annotated
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import date
from ..auth import get_current_user
from ..data import database
from ..biz import roomsHelper as helper
from .. import utils

######## Logging ########
logger = logging.getLogger("tww.service.rooms")

router = APIRouter(
    prefix="/rooms",  # all routes start with /rooms
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

class BookingModel (BaseModel):
    booking_id: int
    room_id: int
    check_in: date
    check_out: date
    number_of_people: int
    customer_name: str
    booking_date: date
    booked_by: str
    status: str
    room_price: float
    discount_price: float
    service_price: float
    camp_fire: bool
    barbeque: bool
    breakfast: bool

@router.get("/", response_model= None)
async def listRooms(current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["self"]) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    rooms = helper.getAllRooms()
    return {
        "status": status.HTTP_200_OK,
        "rooms": rooms
    }

@router.get("/{room_name}", response_model= None)
async def getRoomByName(room_name: str, current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["self"]) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    room = helper.getRoomByName(room_name)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return {
        "status": status.HTTP_200_OK,
        "room": room
    }

@router.post("/create")
async def createRoom(room: RoomModel, current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        helper.createRoom(room.model_dump())
        return {
            "status": status.HTTP_200_OK,
            "message": "Room created successfully"
        }

    except Exception as e:
        logger.error (f"Exception in createRoom: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to create the room")

@router.get("/checkRoomAvailability/{check_in_date}/{check_out_date}/{number_of_people}", description = "Check room availability based on check-in date, check-out date and number of people")
async def check_room_availability(
        check_in_date: date = Path(..., description="Check-in date in YYYY-MM-DD format", example = "2025-09-27"), 
        check_out_date: date = Path(..., description="Check-out date in YYYY-MM-DD format always greater than the check in date", example = "2025-09-29"), 
        number_of_people: int = Path(..., description="Number of people to be greater than zero", example = 2),
        current_user: dict = Depends(get_current_user)
        ):
    if utils.isAuthorized(current_user, ["manager", 'agent', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    available_rooms = helper.getAvailableRooms(check_in_date, check_out_date, number_of_people)

    return {
        "status": status.HTTP_200_OK,
        "available_rooms": available_rooms or []
    }


@router.post("/bookRoom")
def book_room(booking: BookingModel, current_user: str = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["manager", 'agent', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        bookingDict = booking.model_dump()
        bookingDict["booked_by"] = current_user
        helper.bookRoom(bookingDict)
        return {"message": "Room booked successfully"}
    except Exception as e:
        logger.error(f"Exception in book_room: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to book the room")
