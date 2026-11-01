from . import database
import traceback
import logging
from datetime import date
####### Logger ############
logger = logging.getLogger("tww.service.roomsdb")

def queryAllRoomsDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        return rooms
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
        return room
    except Exception as e:
        logger.error(f"Exception in createRoomDB: {e}")
        traceback.print_exc()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    

def queryRoomByNameDB(room_name):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms WHERE room_name = %s", (room_name,))
        room = cursor.fetchone()
        return room
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryRoomById(room_id):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        return room
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryRolesDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role_id, role_name FROM roles")
        roles = cursor.fetchall()
        return roles
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

