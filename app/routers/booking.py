from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Annotated
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import date
from ..auth import get_current_user
from ..data import database
from ..biz import bookingHelper as helper, BizExceptions as exceptions
from .. import utils

######## Logging ########
logger = logging.getLogger("tww.service.booking")

router = APIRouter(
    prefix="/api/v1/booking",  # all routes start with /api/v1/rooms
    tags=["Booking"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

class BookingModel(BaseModel):
    booked_by_id: int
    booking_id: int
    room_id: int
    customer_id: int
    booking_date: date
    check_in: date
    check_out: date
    number_of_people: int
    number_of_nights: int
    status: str
    source_of_booking_id: int
    room_price: float
    advance_payment: float
    advance_paid_to: int
    advance_payment_method: str
    food_price: float
    service_price: float
    balance_to_pay: float
    is_balance_paid: bool
    balance_paid_to: int
    balance_payment_method: str
    commission: float
    tax_percent: float = 0
    tax_price: float = 0
    discount_price: float = 0
    is_commission_settled: bool
    total_price: float
    final_price_paid_to: int
    is_final_price_paid: bool
    final_price_payment_method: str
    remarks: str

@router.get("/checkRoomAvailability", description = "Check room availability based on check-in date, check-out date and number of people")
async def check_room_availability(
    check_in_date: date = Query(..., description="Check-in date in YYYY-MM-DD format", example = "2025-09-27"), 
    check_out_date: date = Query(..., description="Check-out date in YYYY-MM-DD format always greater than the check in date", example = "2025-09-29"), 
    number_of_people: int = Query(..., description="Number of people to be greater than zero", example = 2),    
    current_user: dict = Depends(get_current_user)):

    if utils.isAuthorized(current_user, ["manager", 'agent', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    available_rooms = helper.getAvailableRooms(check_in_date, check_out_date, number_of_people)

    return {
        "status": status.HTTP_200_OK,
        "available_rooms": available_rooms or []
    }

@router.post("/updateBooking")
def update_booking(booking: BookingModel, current_user: str = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["manager", 'agent', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        bookingDict = booking.model_dump()
        bookingDict["booked_by"] = current_user
        booking = helper.bookRoom(bookingDict, is_update=True)
        return {
            "status": status.HTTP_200_OK,
            "message": "Booking updated successfully", 
            "booking": booking
        }
    except helper.RoomNotAvailableException as e:
        logger.error(f"Room Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room Not Available")
    except exceptions.UserNotAvailableException as e:
        logger.error(f"Booking User Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking User Not Available")
    except exceptions.CustomerNotAvailableException as e:
        logger.error(f"Customer Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer Not Available")
    except Exception as e:
        logger.error(f"Exception in book_room: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to book the room")

@router.post("/createBooking")
def book_room(booking: BookingModel, current_user: str = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["manager", 'agent', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        bookingDict = booking.model_dump()
        bookingDict["booked_by"] = current_user
        booking = helper.bookRoom(bookingDict, is_update=False)
        return {
            "status": status.HTTP_200_OK,
            "message": "Room booked successfully", 
            "booking": booking
        }
    except helper.RoomNotAvailableException as e:
        logger.error(f"Room Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room Not Available")
    except exceptions.UserNotAvailableException as e:
        logger.error(f"Booking User Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking User Not Available")
    except exceptions.CustomerNotAvailableException as e:
        logger.error(f"Customer Not Available Exception in book_room: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer Not Available")
    except Exception as e:
        logger.error(f"Exception in book_room: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to book the room")

@router.get("/listBookingsByCheckInDate/{checkInDate}", description = "list all the bookings since the date, if the date is not provided the default date is since Jan 1, 2020")
async def listBookingsByCheckInDate(
    checkInDate: date = Path(description="Starting date in YYYY-MM-DD format", example = "2025-09-27"), 
    current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin", 'manager', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        bookings = helper.listBookingsSince(checkInDate, is_check_in_date=True)
        return {
            "status": status.HTTP_200_OK,
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Exception in listAllBookings: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to get all the bookings")

@router.get("/listAllBookings", description = "list all the bookings since the date, if the date is not provided the default date is since Jan 1, 2020")
async def listAllBookings(
    current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin", 'manager', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        bookings = helper.listBookingsSince()
        return {
            "status": status.HTTP_200_OK,
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Exception in listAllBookings: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to get all the bookings")

@router.get("/listAllBookings/{startingDate}", description = "list all the bookings since the date, if the date is not provided the default date is since Jan 1, 2020")
async def listAllBookings(
    startingDate: date = Path(description="Starting date in YYYY-MM-DD format", example = "2025-09-27"), 
    current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin", 'manager', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        bookings = helper.listBookingsSince(startingDate)
        return {
            "status": status.HTTP_200_OK,
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Exception in listAllBookings: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to get all the bookings")
    
@router.get("/guestsForDay/{forDate}")
def noOfGuest(forDate: date, current_user: dict = Depends(get_current_user)):
    if utils.isAuthorized(current_user, ["admin", 'manager', 'owner']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    result = helper.guestsForDay(forDate)

    print(result)
    return result

