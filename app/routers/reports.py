from fastapi import APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..data import database
import logging

router = APIRouter(
    prefix="/api/v1/reports",  # all routes start with /api/v1/reports
    tags=["Reports"]    # OpenAPI grouping
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
####### Logger ############
logger = logging.getLogger("tww.service.reports")

@router.get("/reportBookings", description="Gets a report of bookings")
@limiter.limit("10/second")
def report_bookings(request: Request):
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
