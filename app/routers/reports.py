from fastapi import APIRouter
from ..data import database

router = APIRouter()

@router.get("/reportBookings")
def report_bookings():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT username, COUNT(*) as total_bookings
        FROM bookings
        GROUP BY username
    """)
    report = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"report": report}
