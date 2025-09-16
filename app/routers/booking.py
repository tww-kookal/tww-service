from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Annotated
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import date
from .. import auth
from ..biz import bookingHelper as helper, BizExceptions as exceptions

######## Logging ########
logger = logging.getLogger("tww.service.booking")

router = APIRouter(
    prefix="/api/v1/booking",  # all routes start with /api/v1/rooms
    tags=["Booking"]    # OpenAPI grouping
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
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
    food_price: float
    service_price: float
    tax_percent: float = 0
    tax_price: float = 0
    discount_price: float = 0
    total_price: float
    commission_percent: float
    commission: float
    is_commission_settled: bool
    remarks: str

@router.get("/checkRoomAvailability", description = "Check room availability based on check-in date, check-out date and number of people")
@limiter.limit("1/second")
async def check_room_availability(
    request: Request,
    check_in_date: date = Query(..., description="Check-in date in YYYY-MM-DD format", example = "2025-09-27"), 
    check_out_date: date = Query(..., description="Check-out date in YYYY-MM-DD format always greater than the check in date", example = "2025-09-29"), 
    number_of_people: int = Query(..., description="Number of people to be greater than zero", example = 2),    
    authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):

    available_rooms = helper.getAvailableRooms(check_in_date, check_out_date, number_of_people, None)

    return {
        "status": status.HTTP_200_OK,
        "available_rooms": available_rooms or []
    }

@router.post("/updateBooking")
@limiter.limit("1/second")
def update_booking(request: Request, booking: BookingModel,authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
    try:
        bookingDict = booking.model_dump()
        bookingDict["booked_by"] = authorized_user['user_name']
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
@limiter.limit("1/second")
def book_room(request: Request, booking: BookingModel,authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
    try:
        bookingDict = booking.model_dump()
        bookingDict["booked_by"] = authorized_user['user_name']
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
@limiter.limit("5/second")
async def listBookingsByCheckInDate(
    request: Request,
    checkInDate: date = Path(description="Starting date in YYYY-MM-DD format", example = "2025-09-27"), 
    authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
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
@limiter.limit("1/second")
async def listAllBookings(
    request: Request,
    authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
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
@limiter.limit("1/second")
async def listAllBookings(
    request: Request,
    startingDate: date = Path(description="Starting date in YYYY-MM-DD format", example = "2025-09-27"), 
    authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
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
@limiter.limit("1/second")
def noOfGuest(request: Request, forDate: date, authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
    result = helper.guestsForDay(forDate)
    print(result)
    return result

@router.get("/byID/{booking_id}", description = "list all the bookings since the date, if the date is not provided the default date is since Jan 1, 2020")
@limiter.limit("1/second")
async def getBookingByID(
    request: Request,
    booking_id: int = Path(description="Booking ID", example = 1), 
    authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
    try:
        booking = helper.getBookingByID(booking_id)
        return {
            "status": status.HTTP_200_OK,
            "booking": booking
        }
    except helper.BookingNotFoundException as e:
        logger.error(f"Booking Not Found Exception in getBookingByID: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking Not Found")
    except Exception as e:
        logger.error(f"Exception in getBookingByID: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to get all the bookings")