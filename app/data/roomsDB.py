from . import database
import traceback
import logging
from datetime import date
####### Logger ############
logger = logging.getLogger("tww.service.roomsdb")

def queryAllRoomsDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return rooms

def createRoomDB(room):
    conn = database.get_connection()
    try:
        duplicateRoom = queryRoomByNameDB(room["room_name"])
        if duplicateRoom is not None:
            logger.info(f"Room Already Exists")
            raise Exception("Room Already Exists")

        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms) VALUES (%s, %s, %s, %s, %s)",
                   (room["room_name"], room["min_capacity"], room["max_capacity"], room["number_of_beds"], room["number_of_bathrooms"]))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Exception in createRoomDB: {e}")
        traceback.print_exc()
        raise e

def queryRoomByNameDB(room_name):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE room_name = %s", (room_name,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    return room

def queryAvailableRoomsDB(check_in, check_out, number_of_people):
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
    cursor.close()
    conn.close()
    return available_rooms

def persistBookingDB(booking: dict):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (customer_id, room_id, check_in, check_out, booking_date, booked_by, status, room_price, food_price, service_price, tax_price, discount_price, total_price) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (booking["customer_id"], booking["room_id"], booking["check_in"], booking["check_out"], booking["booking_date"], booking["booked_by"], booking["status"], booking["room_price"], booking["food_price"], booking["service_price"], booking["tax_price"], booking["discount_price"], booking["total_price"]))
    conn.commit()
    cursor.close()
    conn.close()

def queryRolesDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role_id, role_name FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return roles

def listBookingsSinceDB(startingDate: date):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT b.booking_id, b.customer_id, c.full_name as "customer_name", c.phone as "contact_number",
            c.email as "contact_email", DATEDIFF(b.check_out, b.check_in) as "number_of_nights",
            b.room_id, r.room_name, b.number_of_people, b.check_in, b.check_out, b.status, b.booking_date, 
            b.booked_by as "booked_by_id", CONCAT(bu.first_name, " ", bu.last_name) as "source_of_booking", 
            b.room_price, b.advance_payment, b.advance_paid_to as "advance_paid_to_id", 
            CONCAT(ba.first_name, ' ', ba.last_name) as "advance_paid_to", 
            b.advance_payment_method, 
            b.food_price, b.service_price, b.tax_price, b.discount_price, b.total_price, 
            b.final_price_paid_to as "final_price_paid_to_id", 
            CONCAT(bp.first_name, ' ', bp.last_name) as "final_price_paid_to", 
            b.final_price_payment_method, b.commission, b.is_commission_settled, b.remarks
        FROM bookings b INNER JOIN customers c ON (b.customer_id = c.customer_id)
        INNER JOIN rooms r ON (b.room_id = r.room_id)
        INNER JOIN users bu on (b.booked_by = bu.user_id)
        LEFT JOIN users ba on (b.advance_paid_to = ba.user_id)
        LEFT JOIN users bp on (b.final_price_paid_to = bp.user_id)
        WHERE b.booking_date >= %s
    """
    cursor.execute(query, (startingDate,))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return bookings
