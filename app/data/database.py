import mysql.connector
from mysql.connector import pooling
from ..config.config import settings
import logging
#import mariadb
####### Logger ############
logger = logging.getLogger("tww.service.database")

dbconfig = {
    'host' : settings.MYSQL_HOST,
    'user' : settings.MYSQL_USER,
    'password' : settings.MYSQL_PASSWORD,
    'database' : settings.MYSQL_DATABASE,
    'port' : settings.MYSQL_PORT,
    'charset' : "utf8mb4",
    'collation' : "utf8mb4_general_ci"            
}

        #     host=settings.MYSQL_HOST,
        #     port=settings.MYSQL_PORT,
        #     user=settings.MYSQL_USER,
        #     password=settings.MYSQL_PASSWORD,
        #     database=settings.MYSQL_DATABASE,
        #     ssl_verify_cert=True

# Connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)

def get_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise e
