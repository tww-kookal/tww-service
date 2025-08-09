from ..data import roomsDB
import traceback

def getAllRooms():
    try:
        return roomsDB.queryAllRoomsDB()
    except Exception as e:
        print ("Exception in getAllRooms: ", e)
        traceback.print_exc()
        return []


def createRoom(room):
    print("Received Room ", room)
    try:
        roomsDB.createRoomDB(room)
        return []
    except Exception as e:
        print ("Exception in createRoom: ", e)
        traceback.print_exc()
        raise Exception("Not able to create the room")

def getRoomByName(room_name: str):
    try:
        return roomsDB.queryRoomByNameDB(room_name)
    except Exception as e:
        print ("Exception in getRoomByName: ", e)
        traceback.print_exc()
        return None

def getAvailableRooms(check_in, check_out, number_of_people):
    try:
        available_rooms = roomsDB.queryAvailableRoomsDB(check_in, check_out, number_of_people)
        return available_rooms
    except Exception as e:
        print ("Exception in getAvailableRooms: ", e)
        traceback.print_exc()
        return []
