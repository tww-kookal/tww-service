from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from ..data import database

router = APIRouter(
    prefix="/reports",  # all routes start with /users
    tags=["Reports"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
