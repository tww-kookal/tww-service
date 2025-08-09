import mysql.connector
from ..config.config import settings
import logging
####### Logger ############
logger = logging.getLogger("tww.service.database")

def get_connection():
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )
    return conn
