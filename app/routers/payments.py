from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
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

@router.post("/deleteById/{booking_payment_id}")
def delete_payment(booking_payment_id: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
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


@router.post("/update")
def update_payment(payment: PaymentModel, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
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

@router.post("/add")
def add_payment(payment: PaymentAddModel, authorized_user: dict = Depends(auth.authorizedUser(["manager", 'agent', 'owner'])) ):
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

@router.get("/forBookingID/{booking_id}")
def getPaymentsForBooking(
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