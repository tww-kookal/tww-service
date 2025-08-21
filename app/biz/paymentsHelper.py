from ..data import paymentDB
from .BizExceptions import CustomerNotAvailableException, RoomNotAvailableException, BookingNotFoundException, PaymentExceededException
from . import bookingHelper as bookingHelper, usersHelper as userHelper
import traceback
import logging
from datetime import date

####### Logger ############
logger = logging.getLogger("tww.service.paymentHelper")

def getPaymentsForBooking(booking_id: int):
    payments = paymentDB.queryPaymentsForBooking(booking_id)
    if payments:
        return payments
    else:
        return []

def getTotalBookingPrice(booking_id: int):
    booking = bookingHelper.getBookingById(booking_id)
    if not booking:
        raise BookingNotFoundException(f"Booking ID {booking_id} not found")
    return booking["total_price"] or 0

def addPayment(payment: dict, is_update: bool = False):
    # get existing payments
    paymentsForBooking = getPaymentsForBooking(payment["booking_id"])

    validatePaymentAmount(payment, paymentsForBooking)
    payment["payment_added_by"] = userHelper.getUserByUserName(payment["payment_added_by"])["user_id"]

    if is_update:
        paymentDB.updatePaymentDB(payment)
    else:
        paymentDB.persistPaymentDB(payment)

def validatePaymentAmount(payment: dict, payments: list):
    totalBookingPrice = getTotalBookingPrice(payment["booking_id"])
    paidAmount = 0
    for p in payments:
        if p['payment_for'] == 'refund':
            totalBookingPrice = totalBookingPrice - p["payment_amount"]
        else:
            paidAmount += p["payment_amount"]
    if payment["payment_amount"] > (totalBookingPrice - paidAmount):
        raise PaymentExceededException(f"Payment amount {payment['payment_amount']} exceeds the booking amount {totalBookingPrice}")
    return True
