from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Annotated
import traceback
import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import date
from .. import auth
from ..biz import paymentsHelper as helper, BizExceptions as exceptions
from . import booking as bookingRouter, rooms as roomsRouter

######## Logging ########
logger = logging.getLogger("tww.service.gateway")

router = APIRouter(
    prefix="/api/v1/gateway",  # all routes start with /api/v1/gateway
    tags=["Gateway"]    # OpenAPI grouping  
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

@router.get("/dashboard/", description="Gateway to fetch all the details of the Dashboard")
@limiter.limit("10/second")
async def get_dashboard(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner', 'employee'])) ):
    try:       
        guests_details = await bookingRouter.noOfGuest(request, date.today(), authorized_user)
        bookings_list = await bookingRouter.listBookingsByCheckInDate(request, date.today(), authorized_user)

        dashboard_details = {
            "guests_for_day": guests_details,
            "bookings": bookings_list.get("bookings", [])
        }
        return {
            "status": status.HTTP_200_OK,
            "message": "Dashboard fetched successfully",
            "content": dashboard_details
        }
    except Exception as e:
        logger.error(f"Exception in get_dashboard: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch dashboard details")

@router.get("/availability/{for_date}", description="Gateway to fetch all the details of the Availability ")
@limiter.limit("10/second")
async def get_availability(request: Request, 
                           for_date: date = Path(description="Starting date in YYYY-MM-DD format", example = "2025-09-27"),  
                           authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner', 'employee'])) ):
    try:
        logger.debug(f"Fetching availability for date: {for_date}")
        bookings_list = await bookingRouter.listBookingsByCheckInDate(request, for_date, authorized_user)
        rooms = await roomsRouter.listRooms(request, authorized_user)

        return {
            "status": status.HTTP_200_OK,
            "message": "Availability fetched successfully",
            "content": {
                "bookings": bookings_list.get("bookings", []),
                "rooms": rooms.get("rooms", [])
            }
        }
    except Exception as e:
        logger.error(f"Exception in get_availability: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to fetch availability details")