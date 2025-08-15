import mysql.connector
from ..config.config import settings
import logging
import mariadb
####### Logger ############
logger = logging.getLogger("tww.service.database")

def get_connection():
    # conn = mysql.connector.connect(
    #     host=settings.MYSQL_HOST,
    #     user=settings.MYSQL_USER,
    #     password=settings.MYSQL_PASSWORD,
    #     database=settings.MYSQL_DATABASE
    # )
    # return conn

    try:
        conn = mariadb.connect (
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            ssl_verify_cert=True
        )

        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        raise e
