from . import database
import traceback
import logging
from datetime import date
####### Logger ############
logger = logging.getLogger("tww.service.bookingdb")

def queryAvailableRoomsDB(check_in, check_out, number_of_people):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query  = """
        SELECT r.room_id, r.room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms
        FROM rooms r
        LEFT JOIN bookings b 
            ON r.room_id = b.room_id
            AND (
                b.check_in < %s AND b.check_out > %s
            )
        WHERE b.booking_id IS NULL
        AND %s BETWEEN r.min_capacity AND r.max_capacity
        """
        logger.info(f"Query to fetch available rooms: {query}")
        cursor.execute(query, (check_out, check_in, number_of_people))
        available_rooms = cursor.fetchall()
        return available_rooms
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def listBookingsSinceDB(startingDate: date, is_check_in_date: bool = True):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.booking_id, b.customer_id, c.full_name as "customer_name", c.phone as "contact_number",
                c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
                b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
                b.booked_by_id, 
                IFNULL(b.source_of_booking_id, 0) as source_of_booking_id,
                b.room_price, b.advance_payment, IFNULL(b.advance_paid_to, 0) AS advance_paid_to, 
                CONCAT(ba.first_name, ' ', ba.last_name) as "advance_paid_to_user", 
                CONCAT(bs.first_name, ' ', bs.last_name) as "source_of_booking", 
                b.advance_payment_method, 
                b.food_price, b.service_price, b.tax_price, b.discount_price, b.total_price, 
                IFNULL(b.final_price_paid_to, 0) as final_price_paid_to, 
                CONCAT(bp.first_name, ' ', bp.last_name) as "final_price_paid_to_user", 
                b.final_price_payment_method, b.commission, b.is_commission_settled, b.remarks,
                b.balance_to_pay, b.is_balance_paid, IFNULL(b.balance_paid_to, 0) as balance_paid_to, b.balance_payment_method,
                CONCAT(bb.first_name, ' ', bb.last_name) as "balance_paid_to_user", b.is_final_price_paid
            FROM bookings b INNER JOIN customers c ON (b.customer_id = c.customer_id)
            INNER JOIN rooms r ON (b.room_id = r.room_id)
            LEFT JOIN users ba on (b.advance_paid_to = ba.user_id)
            LEFT JOIN users bp on (b.final_price_paid_to = bp.user_id)
            LEFT JOIN users bs on (b.source_of_booking_id = bs.user_id)
            LEFT JOIN users bb on (b.balance_paid_to = bb.user_id)
        """

        if is_check_in_date:
            query += " WHERE b.check_in >= %s OR b.check_out = %s"
            cursor.execute(query, (startingDate, startingDate, ))
        else:
            query += " WHERE b.booking_date >= %s"
            cursor.execute(query, (startingDate,))

        bookings = cursor.fetchall()
        return bookings
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def guestsForDay(forDate: date):
    try:
        conn =database.get_connection()
        cursor = conn.cursor()
        query = 'SELECT SUM(number_of_people) as "number_of_guests" FROM bookings WHERE  %s BETWEEN check_in AND check_out'
        cursor.execute(query, (forDate,))
        result = cursor.fetchone()
        return result
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getBookingById(booking_id : int ):
    try:
        conn =database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.booking_id, b.customer_id, c.full_name as "customer_name", c.phone as "contact_number",
                c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
                b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
                b.booked_by_id, 
                IFNULL(b.source_of_booking_id, 0) as source_of_booking_id,
                b.room_price, b.advance_payment, IFNULL(b.advance_paid_to, 0) AS advance_paid_to, 
                CONCAT(ba.first_name, ' ', ba.last_name) as "advance_paid_to_user", 
                CONCAT(bs.first_name, ' ', bs.last_name) as "source_of_booking", 
                b.advance_payment_method, 
                b.food_price, b.service_price, b.tax_price, b.discount_price, b.total_price, 
                IFNULL(b.final_price_paid_to, 0) as final_price_paid_to, 
                CONCAT(bp.first_name, ' ', bp.last_name) as "final_price_paid_to_user", 
                b.final_price_payment_method, b.commission, b.is_commission_settled, b.remarks,
                b.balance_to_pay, b.is_balance_paid, IFNULL(b.balance_paid_to, 0) as balance_paid_to, b.balance_payment_method,
                CONCAT(bb.first_name, ' ', bb.last_name) as "balance_paid_to_user", b.is_final_price_paid
            FROM bookings b INNER JOIN customers c ON (b.customer_id = c.customer_id)
            INNER JOIN rooms r ON (b.room_id = r.room_id)
            LEFT JOIN users ba on (b.advance_paid_to = ba.user_id)
            LEFT JOIN users bp on (b.final_price_paid_to = bp.user_id)
            LEFT JOIN users bs on (b.source_of_booking_id = bs.user_id)
            LEFT JOIN users bb on (b.balance_paid_to = bb.user_id)
            WHERE b.booking_id = %s
        """
        cursor.execute(query, (booking_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def updateBookingDB(booking: dict, is_same_room : bool = False):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE bookings 
            SET customer_id = %s, room_id = %s, number_of_people = %s, check_in = %s, check_out = %s, 
            status = %s, booking_date = %s, booked_by_id = %s, source_of_booking_id = %s, room_price = %s, 
            advance_payment = %s, advance_paid_to = %s, advance_payment_method = %s, food_price = %s,
            service_price = %s, tax_percent = %s, tax_price = %s, discount_price = %s, total_price = %s, final_price_paid_to = %s, 
            is_final_price_paid = %s, final_price_payment_method = %s, commission = %s, is_commission_settled = %s, remarks = %s,
            balance_to_pay = %s, is_balance_paid = %s, balance_paid_to = %s, balance_payment_method = %s
            WHERE booking_id = %s
        """
        cursor.execute(query, (booking["customer_id"], booking["room_id"], booking["number_of_people"], 
                            booking["check_in"], booking["check_out"], booking["status"], 
                            booking["booking_date"], booking["booked_by_id"], 
                            booking["source_of_booking_id"], booking["room_price"],
                            booking["advance_payment"], booking["advance_paid_to"],
                            booking["advance_payment_method"], booking["food_price"], 
                            booking["service_price"], booking["tax_percent"], 
                            booking["tax_price"], booking["discount_price"], booking["total_price"],
                            booking["final_price_paid_to"], booking["is_final_price_paid"],
                            booking["final_price_payment_method"], booking["commission"], 
                            booking["is_commission_settled"], booking["remarks"],
                            booking["balance_to_pay"], booking["is_balance_paid"], 
                            booking["balance_paid_to"], booking["balance_payment_method"],
                            booking["booking_id"]))
        conn.commit()
        return booking
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def persistBookingDB(booking: dict):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO bookings (customer_id, room_id, number_of_people, check_in, check_out, 
            status, booking_date, booked_by_id, source_of_booking_id, room_price, 
            advance_payment, advance_paid_to, advance_payment_method, food_price,
            service_price, tax_percent, tax_price, discount_price, total_price, final_price_paid_to, 
            is_final_price_paid, final_price_payment_method, commission, is_commission_settled, remarks,
            balance_to_pay, is_balance_paid, balance_paid_to, balance_payment_method)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        cursor.execute(query, (booking["customer_id"], booking["room_id"], booking["number_of_people"], 
                            booking["check_in"], booking["check_out"], booking["status"], 
                            booking["booking_date"], booking["booked_by_id"], 
                            booking["source_of_booking_id"], booking["room_price"],
                            booking["advance_payment"], booking["advance_paid_to"],
                            booking["advance_payment_method"], booking["food_price"], 
                            booking["service_price"], booking["tax_percent"], 
                            booking["tax_price"], booking["discount_price"], booking["total_price"],
                            booking["final_price_paid_to"], booking["is_final_price_paid"],
                            booking["final_price_payment_method"], booking["commission"], 
                            booking["is_commission_settled"], booking["remarks"],
                            booking["balance_to_pay"], booking["is_balance_paid"], 
                            booking["balance_paid_to"], booking["balance_payment_method"]))
        booking["booking_id"] = cursor.lastrowid
        conn.commit()
        return booking
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
