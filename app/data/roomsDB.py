from . import database
import traceback

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
            print("Room Already Exists")
            raise Exception("Room Already Exists")

        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms) VALUES (%s, %s, %s, %s, %s)",
                   (room["room_name"], room["min_capacity"], room["max_capacity"], room["number_of_beds"], room["number_of_bathrooms"]))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print ("Exception in createRoomDB: ", e)
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
        SELECT r.room_name, min_capacity, max_capacity, number_of_beds, number_of_bathrooms
        FROM rooms r
        LEFT JOIN bookings b 
            ON r.room_id = b.room_id
            AND (
                b.check_in < %s AND b.check_out > %s
            )
        WHERE b.booking_id IS NULL
        AND %s BETWEEN r.min_capacity AND r.max_capacity
    """
    print("Query to fetch available rooms", query)
    cursor.execute(query, (check_out, check_in, number_of_people))
    available_rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return available_rooms
