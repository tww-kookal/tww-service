from ..data import roomsDB, usersDB
import traceback
import logging
from datetime import date

####### Logger ############
logger = logging.getLogger("tww.service.roomshelper")

def getAllRooms():
    try:
        return roomsDB.queryAllRoomsDB()
    except Exception as e:
        logger.error(f"Exception in getAllRooms: {e}")
        traceback.print_exc()
        return []


def createRoom(room):
    logger.info(f"Received Room: {room}")
    try:
        roomsDB.createRoomDB(room)
        return []
    except Exception as e:
        logger.error(f"Exception in createRoom: {e}")
        traceback.print_exc()
        raise Exception("Not able to create the room")

def getRoomByName(room_name: str):
    try:
        return roomsDB.queryRoomByNameDB(room_name)
    except Exception as e:
        logger.error(f"Exception in getRoomByName: {e}")
        traceback.print_exc()
        return None

def getAvailableRooms(check_in, check_out, number_of_people):
    try:
        available_rooms = roomsDB.queryAvailableRoomsDB(check_in, check_out, number_of_people)
        return available_rooms
    except Exception as e:
        logger.error(f"Exception in getAvailableRooms: {e}")
        traceback.print_exc()
        return []

def bookRoom(booking: dict):
    try:

        bookedUser = usersDB.queryUserDB(booking["booked_by"])
        if not bookedUser:
            logger.info(f"Booking User not found")
            raise Exception("Booking User not found")

        availableRooms = roomsDB.queryAvailableRoomsDB(
            booking["check_in"], booking["check_out"], booking["number_of_people"]
        )
        if not availableRooms or len(availableRooms) == 0:
            logger.info(f"No available rooms for the given date range")
            raise Exception("No available rooms")
        
        isRoomAvailable = False
        
        for availableRoom in availableRooms :
            if availableRoom["room_id"] == booking["room_id"]:
                booking["room_name"] = availableRoom["room_name"]
                isRoomAvailable = True
                break

        if isRoomAvailable == False:
            logger.info(f"Selected Room not available")
            raise Exception("Selected Room not available")
        
        booking["booked_by"] = bookedUser["user_id"]
        booking["customer_id"] = 1
        booking["food_price"] = 0.0
        booking["tax_price"] = 0.0
        booking["discount_price"] = 0.0
        booking["total_price"] = 0.0
        
        logger.info(f"Persisting Booking Room: {booking}")
        roomsDB.persistBookingDB(booking)
    except Exception as e:
        logger.error(f"Exception in bookRoom: {e}")
        traceback.print_exc()
        raise Exception("Not able to book the room")

def listBookingsSince(startingDate: date = date(2020, 1, 1)):
    try:
        return roomsDB.listBookingsSinceDB(startingDate)
    except Exception as e:
        logger.error(f"Exception in listAllBookings: {e}")
        traceback.print_exc()
        return []

def guestsForDay(forDate: date):
    try:
        return roomsDB.guestsForDay(forDate=forDate)[0]
    except Exception as e:
        logger.error(f"Exception in no_of_guest: {e}")
        traceback.print_exc()
        raise Exception("Not able to get the number of guests")
