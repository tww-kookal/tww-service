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
        room["room_id"] = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return room
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

def queryRoomById(room_id):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    return room

def queryRolesDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role_id, role_name FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return roles

