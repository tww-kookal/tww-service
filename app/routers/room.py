from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..data import database

router = APIRouter()

@router.get("/checkRoomAvailability")
def check_room_availability(check_in: str, check_out: str):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT room_id, room_name 
        FROM rooms 
        WHERE room_id NOT IN (
            SELECT room_id FROM bookings 
            WHERE check_in < %s AND check_out > %s
        )
    """, (check_out, check_in))
    available_rooms = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"available_rooms": available_rooms}

@router.post("/bookRoom")
def book_room(room_id: int, check_in: str, check_out: str, current_user: str = Depends(get_current_user)):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (room_id, username, check_in, check_out)
        VALUES (%s, %s, %s, %s)
    """, (room_id, current_user, check_in, check_out))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Room booked successfully"}
