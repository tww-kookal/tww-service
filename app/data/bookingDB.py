from . import database
import traceback
import logging
from datetime import date
####### Logger ############
logger = logging.getLogger("tww.service.bookingdb")

def queryAvailableRoomsDB(check_in, check_out, number_of_people, room_id):
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

        if room_id:
            query += " AND r.room_id = %s"
        else:
            query += " AND r.room_type IS NOT NULL"
            
        logger.info(f"Query to fetch available rooms: {query}, PARAMETERS: {(check_in, check_out, number_of_people, room_id)}")
        cursor.execute(query, (check_in, check_out, number_of_people, room_id))
        available_rooms = cursor.fetchall()
        logger.debug(f"Available rooms: {available_rooms}")
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
            SELECT b.booking_id, b.customer_id, CONCAT(c.first_name, ' ', c.last_name) as "customer_name", c.phone as "contact_number",
                c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
                b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
                b.booked_by_id, IFNULL(b.source_of_booking_id, 0) as source_of_booking_id,
                CONCAT(bs.first_name, ' ', bs.last_name) as "source_of_booking", b.total_price,
                b.room_price, b.food_price, b.service_price, b.tax_price, b.discount_price, 
                b.is_commission_settled, b.remarks, b.commission, b.commission_percent
            FROM bookings b INNER JOIN users c ON (b.customer_id = c.user_id)
            INNER JOIN rooms r ON (b.room_id = r.room_id)
            LEFT JOIN users bs on (b.source_of_booking_id = bs.user_id)
        """

        if is_check_in_date:
            query += " WHERE b.check_in >= %s"
            cursor.execute(query, (startingDate, ))
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
            SELECT b.booking_id, b.customer_id, CONCAT(c.first_name, ' ', c.last_name) as "customer_name", c.phone as "contact_number",
                c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
                b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
                b.booked_by_id, IFNULL(b.source_of_booking_id, 0) as source_of_booking_id,
                CONCAT(bs.first_name, ' ', bs.last_name) as "source_of_booking", b.total_price, 
                b.room_price, b.food_price, b.service_price, b.tax_price, b.discount_price, 
                b.is_commission_settled, b.remarks, b.commission, b.commission_percent
            FROM bookings b INNER JOIN users c ON (b.customer_id = c.user_id)
            INNER JOIN rooms r ON (b.room_id = r.room_id)
            LEFT JOIN users bs on (b.source_of_booking_id = bs.user_id)
            WHERE b.booking_id = %s
        """
        cursor.execute(query, (booking_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def search_bookings(search_criteria: dict):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        params = []
        
        query = """
            SELECT b.booking_id, b.customer_id, CONCAT(c.first_name, ' ', c.last_name) as "customer_name", c.phone as "contact_number",
                c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
                b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
                b.booked_by_id, IFNULL(b.source_of_booking_id, 0) as source_of_booking_id,
                CONCAT(bs.first_name, ' ', bs.last_name) as "source_of_booking", b.total_price,
                b.room_price, b.food_price, b.service_price, b.tax_price, b.discount_price, 
                b.is_commission_settled, b.remarks, b.commission, b.commission_percent
            FROM bookings b INNER JOIN users c ON (b.customer_id = c.user_id)
            INNER JOIN rooms r ON (b.room_id = r.room_id)
            LEFT JOIN users bs on (b.source_of_booking_id = bs.user_id)
            WHERE 1=1 
        """
        if 'from_date' in search_criteria and 'to_date' in search_criteria:
            query += " AND ((b.check_in BETWEEN %s AND %s) OR (b.check_out BETWEEN %s AND %s))"
            params.extend([search_criteria['from_date'], search_criteria['to_date'], search_criteria['from_date'], search_criteria['to_date']])

        if 'guest_name' in search_criteria:
            query += " AND CONCAT(c.first_name, ' ', c.last_name) LIKE %s"
            params.append(f"%{search_criteria['guest_name']}%")
        
        if 'source_of_booking_id' in search_criteria:
            query += " AND b.source_of_booking_id = %s"
            params.append(search_criteria['source_of_booking_id'])

        if 'guest_phone' in search_criteria:
            query += " AND c.phone LIKE %s"
            params.append(f"%{search_criteria['guest_phone']}%")
        
        query += " ORDER BY check_in ASC"
        cursor.execute(query, tuple(params))
        bookings = cursor.fetchall()
        return bookings
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
            food_price = %s, service_price = %s, tax_percent = %s, tax_price = %s, discount_price = %s,
            total_price = %s, commission_percent = %s, commission = %s, is_commission_settled = %s, 
            remarks = %s
            WHERE booking_id = %s
        """
        cursor.execute(query, (booking["customer_id"], booking["room_id"], booking["number_of_people"], 
                            booking["check_in"], booking["check_out"], booking["status"].lower(), 
                            booking["booking_date"], booking["booked_by_id"], 
                            booking["source_of_booking_id"], booking["room_price"],                            
                            booking["food_price"], booking["service_price"], booking["tax_percent"], 
                            booking["tax_price"], booking["discount_price"], booking["total_price"],
                            booking['commission_percent'],booking["commission"], booking["is_commission_settled"], 
                            booking["remarks"], booking["booking_id"]))
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
            food_price, service_price, tax_percent, tax_price, discount_price, total_price,
            commission_percent, commission, is_commission_settled, remarks)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """

        parameters = (booking["customer_id"], booking["room_id"], booking["number_of_people"], 
                            booking["check_in"], booking["check_out"], booking["status"].lower(), 
                            booking["booking_date"], booking["booked_by_id"], 
                            booking["source_of_booking_id"], booking["room_price"], booking["food_price"], 
                            booking["service_price"], booking["tax_percent"], 
                            booking["tax_price"], booking["discount_price"], booking["total_price"],
                            booking['commission_percent'],booking["commission"], booking["is_commission_settled"], 
                            booking["remarks"],)
        
        cursor.execute(query, parameters)
        booking["booking_id"] = cursor.lastrowid
        conn.commit()
        return booking
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()