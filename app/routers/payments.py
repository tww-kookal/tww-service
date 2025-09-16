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

######## Logging ########
logger = logging.getLogger("tww.service.payments")

router = APIRouter(
    prefix="/api/v1/payment",  # all routes start with /api/v1/payment
    tags=["Payments"]    # OpenAPI grouping
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

class PaymentAddModel (BaseModel):
    booking_id: int
    payment_amount: float
    payment_date: date
    payment_for: str
    payment_to: int
    payment_type: str
    remarks: str

class PaymentModel(PaymentAddModel):
    booking_payments_id: int

@router.post("/deleteById/{booking_payment_id}", description="Deletes a payment by ID")
@limiter.limit("1/second")
def delete_payment(request: Request, booking_payment_id: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
    try:
        helper.deletePayment(booking_payment_id)
        return {
            "status": status.HTTP_200_OK,
            "message": "Payment deleted successfully"
        }
    except Exception as e:
        logger.error(f"Exception in delete_payment: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to delete the payment")


@router.post("/update", description="Updates a payment")
@limiter.limit("1/second")
def update_payment(request: Request, payment: PaymentModel, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
    try:
        paymentDict = payment.model_dump()
        paymentDict["payment_added_by"] = authorized_user['user_name']
        payment = helper.addPayment(paymentDict, is_update=True)
        return {
            "status": status.HTTP_200_OK,
            "message": "Payment updated successfully"
        }
    except Exception as e:
        logger.error(f"Exception in update_payment: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to update the payment")

@router.post("/add", description="Adds a new payment")
@limiter.limit("1/second")
def add_payment(request: Request, payment: PaymentAddModel, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
    try:
        paymentDict = payment.model_dump()
        paymentDict["payment_added_by"] = authorized_user['user_name']
        payment = helper.addPayment(paymentDict, is_update=False)
        return {
            "status": status.HTTP_200_OK,
            "addedPayment": payment
        }
    except exceptions.BookingNotFoundException as e:
        logger.error(f"Booking Not Found Exception in add_payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking Not Found")
    except exceptions.PaymentExceededException as e:
        logger.error(f"Payment Exceeded Exception in add_payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment Exceeded")
    except Exception as e:
        logger.error(f"Exception in book_room: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to book the room")

@router.get("/forBookingID/{booking_id}", description="Gets payments for a booking ID")
@limiter.limit("1/second")
def getPaymentsForBooking(request: Request,
    booking_id: int = Path(description="Booking ID", example = 1), 
    authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager', 'owner']))):
    try:
        payments = helper.getPaymentsForBooking(booking_id)
        return {
            "status": status.HTTP_200_OK,
            "payments": payments,
            "booking_id": booking_id
        }
    except Exception as e:
        logger.error(f"Exception in getPaymentsForBooking: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Not able to get the payments")