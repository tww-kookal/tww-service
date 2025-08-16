import mysql.connector
from ..config.config import settings
import logging
#import mariadb
####### Logger ############
logger = logging.getLogger("tww.service.database")

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            port=settings.MYSQL_PORT,
            charset="utf8mb4",
            collation="utf8mb4_general_ci"            
        )
        return conn

        # conn = mariadb.connect (
        #     host=settings.MYSQL_HOST,
        #     port=settings.MYSQL_PORT,
        #     user=settings.MYSQL_USER,
        #     password=settings.MYSQL_PASSWORD,
        #     database=settings.MYSQL_DATABASE,
        #     ssl_verify_cert=True
        # )

        return conn
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise e
