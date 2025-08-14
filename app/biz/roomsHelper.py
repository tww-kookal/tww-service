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
        return roomsDB.createRoomDB(room)
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
