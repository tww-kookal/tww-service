from ..data import roomsDB, usersDB, customersDB
from .BizExceptions import UserNotAvailableException, CustomerNotAvailableException, RoomNotAvailableException
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

def getUserByID(user_id: str, throw_exception=True):
    user = usersDB.queryUserByIdDB(user_id)
    if not user:
        logger.error(f"User not found")
        if throw_exception:
            raise UserNotAvailableException()
        else:
            return None
    return user

def getUserByUserName(username: str, throw_exception=True):
    user = usersDB.queryUserDB(username)
    if not user:
        logger.error(f"User not found")
        if throw_exception:
            raise UserNotAvailableException()
        else:
            return None
    return user

def getCustomerByID(customer_id: str):
    customer = customersDB.queryCustomerByIDDB(customer_id)
    if not customer:
        logger.error(f"Customer not found")
        raise CustomerNotAvailableException()
    return customer

def getSelectedRoom(check_in: date, check_out: date, number_of_peope: int, room_id: int):
    availableRooms = roomsDB.queryAvailableRoomsDB(
        check_in, check_out, number_of_peope
    )
    if not availableRooms or len(availableRooms) == 0:
        logger.error(f"No available rooms for the given date range")
        raise RoomNotAvailableException()
    
    isRoomAvailable = False
    
    for availableRoom in availableRooms :
        if availableRoom["room_id"] == room_id:
            return availableRoom

    if isRoomAvailable == False:
        logger.info(f"Selected Room not available")
        raise RoomNotAvailableException("Selected Room not available")

def getFullNameOfUserByID(user_id: int):
    user_details = getUserByID(user_id, throw_exception=False)
    logger.info(f"User Full Name of USer By ID {user_id} Details: {user_details}")
    if user_details:
        return user_details["first_name"] + " " + user_details['last_name']
    else:
        return ''

def bookRoom(booking: dict):
    if booking["source_of_booking_id"] == 0 : 
        booking["source_of_booking_id"] = None
    logger.info(f"Received Booking: {booking}")
    customer = getCustomerByID(booking["customer_id"])
    room = getSelectedRoom(booking["check_in"], booking["check_out"], booking["number_of_people"], booking["room_id"])       
    bookingUser = getUserByUserName(booking["booked_by"], throw_exception=True)

    booking["booked_by_id"] = bookingUser["user_id"]
    booking["customer_name"] = customer["customer_name"]
    booking["contact_number"] = customer["phone"]
    booking["booked_by"] = bookingUser["first_name"] + " " + bookingUser['last_name']
    booking["room_name"] = room["room_name"]
    booking["source_of_booking"] = getFullNameOfUserByID(booking["source_of_booking_id"])
    booking["advance_paid_to"] = getFullNameOfUserByID(booking["advance_paid_to"])
    booking["final_price_paid_to"] = getFullNameOfUserByID(booking["final_price_paid_to"])
    booking["balance_paid_to"] = getFullNameOfUserByID(booking["balance_paid_to"])

    logger.info(f"Persisting Booking Room: {booking}")
    return roomsDB.persistBookingDB(booking)

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
