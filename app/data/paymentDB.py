from . import database
import traceback
import logging
from datetime import date
####### Logger ############
logger = logging.getLogger("tww.service.paymentdb")

def queryPaymentsForBooking (booking_id : int):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT booking_payments_id, booking_id, payment_amount, payment_date, payment_to, payment_for, remarks, payment_type
            FROM booking_payments
            WHERE booking_id = %s
            ORDER BY payment_date ASC
        """
        cursor.execute(query, (booking_id,))
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def persistPaymentDB(payment: dict):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO booking_payments (booking_id, payment_amount, payment_date, payment_to,
            payment_type, payment_for, remarks, payment_added_by)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        parameters = (payment["booking_id"], payment["payment_amount"], payment["payment_date"],
            payment["payment_to"], payment["payment_type"].lower(), payment["payment_for"].lower(),
            payment["remarks"], payment["payment_added_by"],)
        
        cursor.execute(query, parameters)
        conn.commit()
        payment["booking_payments_id"] = cursor.lastrowid
        return payment
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def updatePaymentDB(payment: dict):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE booking_payments 
            SET payment_amount = %s, payment_date = %s, payment_to = %s, 
            payment_type = %s, payment_for = %s, remarks = %s, payment_added_by = %s
            WHERE booking_payments_id = %s

        """
        parameters = (payment["payment_amount"], payment["payment_date"],
            payment["payment_to"], payment["payment_type"].lower(), payment["payment_for"].lower(),
            payment["remarks"], payment["payment_added_by"], payment["booking_payments_id"])
        
        cursor.execute(query, parameters)
        conn.commit()
        return payment
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def deletePaymentDB(paymentId: int):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            DELETE FROM booking_payments WHERE booking_payments_id = %s
        """
        parameters = (paymentId,)
        cursor.execute(query, parameters)
        conn.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
